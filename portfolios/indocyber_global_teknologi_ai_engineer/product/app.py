"""Invoice Reader - demo app for the Budgeted Evidence Agent blueprint.

Two pages, no framework, no external assets:
  /          upload or pick a sample, see extracted fields + call budget trace
  /healthz   liveness for tools/deploy_check.py

The extractor here is deliberately simple: it is the *demo*, not the blueprint.
Every field maps to a character offset in the source text so the UI can show the
honest failure state ("not found in this document") instead of guessing.
"""
from __future__ import annotations

import html
import json
import os
import re
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
SAMPLES = ROOT / "samples"
USAGE = ROOT / "usage.json"
CALL_BUDGET = 4
MAX_UPLOAD = 200_000

FIELDS = (
    ("invoice_number", r"(?:invoice|inv|faktur)\s*(?:no|number|#)?\s*[:.]?\s*([A-Z0-9][A-Z0-9/-]{2,})"),
    ("date", r"(?:date|tanggal)\s*[:.]?\s*(\d{1,4}[/-]\d{1,2}[/-]\d{1,4})"),
    ("supplier", r"(?:from|supplier|vendor|dari)\s*[:.]?\s*([A-Za-z][A-Za-z0-9 .,&'-]{2,60})"),
    ("total", r"(?<![A-Za-z])(?:grand\s+total|total\s+due|amount\s+due|jumlah\s+total|total)\s*[:.]?\s*(?:rp\.?|idr|\$)?\s*([\d][\d.,]{2,})"),
)

TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Invoice Reader</title>
<style>
:root{{--bg:#0b0f14;--panel:#121820;--line:#232e3a;--text:#e6edf3;--muted:#93a4b6;
--ok:#3ddc97;--warn:#f5a524;--bad:#ff6b6b;--mono:ui-monospace,Menlo,Consolas,monospace}}
*{{box-sizing:border-box}}body{{margin:0;padding:32px 20px;background:var(--bg);color:var(--text);
font:15px/1.5 "Segoe UI",system-ui,sans-serif}}
main{{max-width:880px;margin:0 auto}}h1{{font-size:22px;margin:0 0 6px}}
.tagline{{color:var(--muted);margin:0 0 24px}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px;margin-bottom:16px}}
.row{{display:flex;gap:12px;flex-wrap:wrap;align-items:center}}
label.file{{flex:1;min-width:240px;border:1px dashed var(--line);border-radius:8px;padding:14px;
color:var(--muted);cursor:pointer;display:block}}
label.file:hover{{border-color:#4cc2ff}}input[type=file]{{display:none}}
.btn{{background:#172029;color:var(--text);border:1px solid var(--line);border-radius:8px;
padding:9px 16px;font-size:14px;cursor:pointer}}.btn:hover{{border-color:#4cc2ff}}
.btn:disabled{{opacity:.45;cursor:not-allowed}}
table{{width:100%;border-collapse:collapse;font-size:14px}}
th{{text-align:left;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);
padding:8px 0;border-bottom:1px solid var(--line)}}
td{{padding:10px 0;border-bottom:1px solid rgba(35,46,58,.6);vertical-align:top}}
.field{{font-family:var(--mono);font-size:12px;color:var(--muted)}}
.value{{font-family:var(--mono)}}.missing{{color:var(--warn)}}
.span{{color:#4cc2ff;text-decoration:none;border-bottom:1px dotted #4cc2ff;cursor:help;font-size:12px}}
.steps{{font-family:var(--mono);font-size:12px;color:var(--muted);display:flex;flex-direction:column;gap:4px}}
.steps b{{color:var(--text);font-weight:500}}
.badge{{font-size:11px;padding:2px 8px;border-radius:999px;border:1px solid var(--line)}}
.badge.ok{{color:var(--ok);border-color:var(--ok)}}.badge.warn{{color:var(--warn);border-color:var(--warn)}}
pre{{white-space:pre-wrap;font-family:var(--mono);font-size:12px;color:var(--muted);margin:0;
max-height:220px;overflow:auto}}
.foot{{color:var(--muted);font-size:12px;margin-top:20px}}
</style></head><body><main>
<h1>Invoice Reader</h1>
<p class="tagline">Upload an invoice, get the fields it can actually prove. Unknown fields say so.</p>
{body}
<p class="foot">Every field links to its source text. The reader stops after {budget} lookups
and refuses instead of guessing.</p>
</main></body></html>"""


def as_record(ts, session, action, **extra):
    return {"ts": ts, "session": session, "action": action, **extra}


def log_usage(session, action, **extra):
    stamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
    record = as_record(stamp, session, action, **extra)
    try:
        with USAGE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def extract(text):
    """Return fields with spans, plus the call trace that produced them."""
    fields, steps = [], []
    calls = 0
    for name, pattern in FIELDS:
        if calls >= CALL_BUDGET:
            steps.append({"step": name, "tool": "lookup", "status": "skipped: budget exhausted"})
            fields.append({"field": name, "value": None, "span": None,
                           "note": "not looked up: budget exhausted"})
            continue
        calls += 1
        match = re.search(pattern, text, re.IGNORECASE)
        if match and match.group(1) and len(match.group(1).strip()) > 1:
            start, end = match.span(1)
            fields.append({"field": name, "value": match.group(1).strip(),
                           "span": [start, end], "note": ""})
            steps.append({"step": name, "tool": "lookup", "status": f"found at {start}-{end}"})
        else:
            fields.append({"field": name, "value": None, "span": None,
                           "note": "not found in this document"})
            steps.append({"step": name, "tool": "lookup", "status": "no admissible span"})
    return fields, steps, calls


def render_result(text, fields, steps, calls, session, source_name):
    rows = []
    for f in fields:
        if f["value"] is None:
            cell = f'<span class="missing">{html.escape(f["note"])}</span>'
        else:
            start, end = f["span"]
            context = html.escape(text[max(0, start - 18):end + 18].replace("\n", " "))
            cell = (f'<span class="value">{html.escape(f["value"])}</span> '
                    f'<a class="span" title="{context}">source [{start}-{end}]</a>')
        rows.append(f'<tr><td class="field">{f["field"]}</td><td>{cell}</td></tr>')

    found = sum(1 for f in fields if f["value"] is not None)
    verdict = "answer" if found == len(fields) else ("partial" if found else "refusal")
    badge = "ok" if verdict == "answer" else "warn"

    trace = "".join(
        f'<div><b>{html.escape(s["step"])}</b> {html.escape(s["status"])}</div>' for s in steps
    )

    body = f"""
<div class="card">
  <div class="row" style="justify-content:space-between">
    <span class="badge {badge}">{verdict}</span>
    <span class="field">{html.escape(source_name)} · {calls}/{CALL_BUDGET} lookups used</span>
  </div>
</div>
<div class="card">
  <table><thead><tr><th>Field</th><th>Value and source</th></tr></thead>
  <tbody>{''.join(rows)}</tbody></table>
</div>
<div class="card"><div class="steps">{trace}</div></div>
<div class="card"><pre>{html.escape(text[:1200])}</pre></div>
<div class="row"><a class="btn" href="/">Read another invoice</a></div>
"""
    log_usage(session, verdict, fields_found=found, fields_total=len(fields), calls=calls)
    return body


def render_home():
    sample_buttons = []
    if SAMPLES.is_dir():
        for path in sorted(SAMPLES.glob("*.txt")):
            label = html.escape(path.stem.replace("_", " "))
            sample_buttons.append(
                f'<form method="post" action="/" style="display:inline">'
                f'<input type="hidden" name="sample" value="{html.escape(path.name)}">'
                f'<button class="btn" type="submit">{label}</button></form>'
            )
    body = f"""
<form class="card" method="post" action="/" enctype="text/plain">
  <div class="row">
    <label class="file">Choose an invoice .txt file, or use a sample below
      <input type="file" id="f" accept=".txt,text/plain">
    </label>
    <button class="btn" id="go" type="submit" disabled>Read invoice</button>
  </div>
  <textarea name="text" id="text" rows="8" style="width:100%;margin-top:14px;background:#0b0f14;
    color:var(--text);border:1px solid var(--line);border-radius:8px;padding:12px;font-family:var(--mono);
    font-size:13px" placeholder="Paste invoice text here..."></textarea>
</form>
<div class="card"><div class="row">{''.join(sample_buttons)}</div></div>
<script>
const file = document.getElementById('f'), text = document.getElementById('text'), go = document.getElementById('go');
function sync(){{ go.disabled = text.value.trim().length < 10; }}
file.addEventListener('change', async () => {{
  const f = file.files[0]; if (!f) return;
  text.value = (await f.text()).slice(0, {MAX_UPLOAD}); sync();
}});
text.addEventListener('input', sync); sync();
</script>
"""
    return body


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def _send(self, status, body, ctype="text/html; charset=utf-8"):
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _session(self):
        cookie = self.headers.get("Cookie") or ""
        match = re.search(r"sid=([a-f0-9]{8,})", cookie)
        if match:
            return match.group(1), False
        return uuid.uuid4().hex, True

    def do_GET(self):
        path = urlparse(self.path).path
        sid, new = self._session()

        if path == "/healthz":
            return self._send(200, json.dumps({"ok": True, "fields": len(FIELDS),
                                               "budget": CALL_BUDGET}), "application/json")

        if path != "/":
            return self._send(404, "not found", "text/plain; charset=utf-8")

        log_usage(sid, "view")
        body = TEMPLATE.format(body=render_home(), budget=CALL_BUDGET)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        if new:
            self.send_header("Set-Cookie", f"sid={sid}; Path=/; HttpOnly; SameSite=Lax")
        payload = body.encode("utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(min(length, MAX_UPLOAD * 2)).decode("utf-8", errors="replace")
        form = parse_qs(raw, keep_blank_values=True)

        sid, _ = self._session()
        text = ""
        source_name = "pasted text"

        if form.get("sample"):
            name = Path(form["sample"][0]).name
            path = SAMPLES / name
            if path.is_file() and path.suffix == ".txt":
                text = path.read_text(encoding="utf-8")
                source_name = path.stem.replace("_", " ")
        else:
            text = (form.get("text") or [""])[0]
            if not text and "text" in raw:
                text = raw.split("text=", 1)[-1]

        text = text.strip()[:MAX_UPLOAD]
        if len(text) < 10:
            body = TEMPLATE.format(
                body='<div class="card"><p class="missing">Paste at least a few lines of invoice text, '
                     'or open a sample.</p><a class="btn" href="/">Back</a></div>',
                budget=CALL_BUDGET,
            )
            return self._send(200, body)

        fields, steps, calls = extract(text)
        body = TEMPLATE.format(
            body=render_result(text, fields, steps, calls, sid, source_name),
            budget=CALL_BUDGET,
        )
        self._send(200, body)


def main():
    port = int(os.environ.get("PORT", "7860"))
    host = os.environ.get("HOST", "0.0.0.0")
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"[+] invoice reader on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
