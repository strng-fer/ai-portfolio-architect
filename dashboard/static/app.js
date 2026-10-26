const state = {
  overview: null,
  sessions: [],
  workflow: null,
  metric: "tokens",
  sort: { key: "updated", dir: -1 },
  timer: null,
};

const $ = (sel) => document.querySelector(sel);

const fmt = (n) => {
  if (n === null || n === undefined) return "–";
  const abs = Math.abs(n);
  if (abs >= 1e9) return (n / 1e9).toFixed(1) + "B";
  if (abs >= 1e6) return (n / 1e6).toFixed(1) + "M";
  if (abs >= 1e3) return (n / 1e3).toFixed(1) + "k";
  return String(n);
};

const ago = (ms) => {
  if (!ms) return "–";
  const s = Math.max(0, Math.round((Date.now() - ms) / 1000));
  if (s < 60) return s + "s ago";
  if (s < 3600) return Math.round(s / 60) + "m ago";
  if (s < 86400) return Math.round(s / 3600) + "h ago";
  return Math.round(s / 86400) + "d ago";
};

const dur = (ms) => {
  if (ms === null || ms === undefined) return "–";
  if (ms < 1000) return ms + "ms";
  if (ms < 60000) return (ms / 1000).toFixed(1) + "s";
  return Math.round(ms / 60000) + "m";
};

const span = (ms) => {
  if (!ms) return "–";
  const m = Math.round(ms / 60000);
  if (m < 60) return m + "m";
  const h = Math.floor(m / 60);
  return h + "h " + (m % 60) + "m";
};

const kb = (bytes) => (bytes ? Math.round(bytes / 1024) + " KB" : "–");

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const fresh = (t) => t.input + t.output + t.reasoning;
const cacheRate = (t) => {
  const denom = t.cache_read + t.input;
  return denom ? t.cache_read / denom : 0;
};

async function getJSON(url) {
  const res = await fetch(url, { cache: "no-store" });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.error || `HTTP ${res.status}`);
  return body;
}

function toast(msg) {
  const el = $("#toast");
  el.textContent = msg;
  el.hidden = false;
  clearTimeout(el._t);
  el._t = setTimeout(() => (el.hidden = true), 4000);
}

function setLive(ok, label) {
  $("#live-dot").className = "dot " + (ok ? "on" : "err");
  $("#scope-label").textContent = label;
}

function renderPipeline() {
  const w = state.workflow;
  if (!w) return;

  $("#pipeline-summary").textContent =
    `${w.counts.portfolios} portfolio(s) · ${w.counts.ready} PDF ready · ${w.counts.jobs} jobs cached`;

  $("#pipeline").innerHTML = w.stages
    .map(
      (s, i) => `<li class="stage ${esc(s.state)}">
        <span class="stage-num">${i + 1}</span>
        <div class="stage-body">
          <span class="stage-label">${esc(s.label)}</span>
          <span class="stage-detail">${esc(s.detail)}</span>
        </div>
      </li>`
    )
    .join("");
}

function renderStats() {
  const o = state.overview;
  const w = state.workflow;
  if (!o) return;
  const t = o.totals;

  const cards = [
    { label: "Sessions", value: fmt(t.sessions), sub: `${o.active_24h} active in 24h` },
    { label: "Fresh tokens", value: fmt(t.tokens_fresh), sub: `${fmt(t.tokens_input)} in / ${fmt(t.tokens_output)} out` },
    { label: "Cache hit", value: (o.cache_hit_rate * 100).toFixed(1) + "%", sub: `${fmt(t.tokens_cache_read)} read` },
    { label: "Tool calls", value: fmt(t.tool_calls), sub: `${t.tool_errors} failed` },
    { label: "Portfolios", value: w ? String(w.counts.portfolios) : "–", sub: w ? `${w.counts.ready} PDF ready` : "" },
    { label: "Tracker rows", value: w ? String(w.counts.tracker) : "–", sub: "portfolio_tracker.csv" },
  ];

  $("#stats").innerHTML = cards
    .map(
      (c) => `<div class="stat">
        <div class="label">${c.label}</div>
        <div class="value">${c.value}</div>
        <div class="sub">${esc(c.sub)}</div>
      </div>`
    )
    .join("");
}

function renderPortfolios() {
  const w = state.workflow;
  if (!w) return;
  const items = w.portfolios;
  $("#portfolio-count").textContent = items.length ? `${items.length} folder(s)` : "";

  if (!items.length) {
    $("#portfolios").innerHTML = `<div class="empty">No blueprint folders yet.</div>`;
    return;
  }

  $("#portfolios").innerHTML = items
    .map((p) => {
      const chip =
        p.status === "READY"
          ? `<span class="tag ok">PDF ready</span>`
          : p.status === "MARKDOWN"
          ? `<span class="tag warn">markdown only</span>`
          : `<span class="tag">draft</span>`;

      const docs = Object.entries(p.docs)
        .map(([name, d]) => {
          const pctW = Math.min(100, (d.words / d.budget) * 100);
          const cls = d.over ? "over" : pctW > 90 ? "near" : "";
          return `<div class="doc-row" title="${esc(name)}: ${d.words}/${d.budget} words">
            <span class="doc-name">${esc(name.slice(0, 2))}</span>
            <span class="track"><span class="fill ${cls}" style="width:${pctW.toFixed(0)}%"></span></span>
            <span class="doc-val">${d.words}/${d.budget}</span>
          </div>`;
        })
        .join("");

      const gates = [];
      gates.push(p.missing.length ? `<span class="tag err">${p.missing.length} doc missing</span>` : `<span class="tag ok">docs complete</span>`);
      if (p.over_budget.length) gates.push(`<span class="tag err">${p.over_budget.length} over budget</span>`);
      if (p.diagrams.length) gates.push(`<span class="tag">${p.diagrams.length} diagrams</span>`);
      if (p.metrics) gates.push(`<span class="tag">${p.metrics} metrics</span>`);
      if (p.prompts) gates.push(`<span class="tag sub">prompt pack</span>`);

      let product = "";
      if (p.product && p.product.mode) {
        product = p.product.ok
          ? `<div class="product-band ok">
               <span class="tag ok">product ready</span>
               <span class="mono">${esc(p.product.audience || "audience unset")}</span>
               ${p.product.url ? `<span class="mono muted">${esc(p.product.url)}</span>` : ""}
             </div>`
          : `<div class="product-band warn">
               <span class="tag warn">product gate</span>
               <span class="muted">${esc(p.product.errors.slice(0, 3).join(" · "))}</span>
             </div>`;
      }

      return `<article class="portfolio">
        <div class="portfolio-head">
          <div class="portfolio-title">
            <strong>${esc(p.title)}</strong>
            <span class="mono muted">${esc(p.slug)}</span>
          </div>
          ${chip}
        </div>
        <div class="portfolio-meta">
          <span><span class="k">mechanism</span> <span class="mono">${esc(p.mechanism)}</span></span>
          <span><span class="k">hours</span> <span class="mono">${p.hours ?? "–"}</span></span>
          <span><span class="k">pdf</span> <span class="mono">${kb(p.pdf_bytes)}</span></span>
          <span><span class="k">tracker</span> <span class="mono">${esc(p.tracker)}</span></span>
          <span><span class="k">updated</span> <span class="mono">${ago(p.updated)}</span></span>
        </div>
        ${product}
        <div class="doc-bars">${docs || `<div class="empty">No documents.</div>`}</div>
        <div class="portfolio-gates">${gates.join("")}</div>
      </article>`;
    })
    .join("");
}

function renderChart() {
  const o = state.overview;
  if (!o) return;
  const days = o.daily;
  if (!days.length) {
    $("#chart").innerHTML = `<div class="empty">No activity recorded yet.</div>`;
    return;
  }

  const metric = state.metric;
  const values = days.map((d) => d[metric] || 0);
  const max = Math.max(...values, 1);

  const W = 720, H = 220, padL = 46, padB = 26, padT = 10, padR = 8;
  const innerW = W - padL - padR;
  const innerH = H - padT - padB;
  const slot = innerW / days.length;
  const barW = Math.max(6, slot * 0.62);

  const grid = [0, 0.25, 0.5, 0.75, 1]
    .map((f) => {
      const gy = padT + innerH - f * innerH;
      return `<line class="gridline" x1="${padL}" y1="${gy}" x2="${W - padR}" y2="${gy}" />
              <text class="tick" x="${padL - 8}" y="${gy + 3}" text-anchor="end">${fmt(Math.round(max * f))}</text>`;
    })
    .join("");

  const bars = days
    .map((d, i) => {
      const v = d[metric] || 0;
      const x = padL + i * slot + (slot - barW) / 2;
      const h = Math.max(v > 0 ? 2 : 0, (v / max) * innerH);
      const tip = `${d.date}\nfresh ${fmt(d.tokens)}  cache ${fmt(d.cache_read)}  tools ${d.tools}`;
      return `<rect class="bar ${metric === "cache_read" ? "cache" : metric === "tools" ? "tools" : ""}"
                x="${x.toFixed(1)}" y="${(padT + innerH - h).toFixed(1)}"
                width="${barW.toFixed(1)}" height="${h.toFixed(1)}" rx="2">
                <title>${esc(tip)}</title>
              </rect>
              <text class="tick" x="${(x + barW / 2).toFixed(1)}" y="${H - 8}" text-anchor="middle">${d.date.slice(5)}</text>`;
    })
    .join("");

  $("#chart").innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Activity per day">
    ${grid}
    <line class="axis" x1="${padL}" y1="${padT + innerH}" x2="${W - padR}" y2="${padT + innerH}" />
    ${bars}
  </svg>`;
}

function renderTools() {
  const tools = state.overview?.tools || [];
  const total = tools.reduce((a, b) => a + b.count, 0);
  $("#tool-total").textContent = total ? `${fmt(total)} calls` : "";
  if (!tools.length) {
    $("#tools").innerHTML = `<div class="empty">No tool calls in this project.</div>`;
    return;
  }
  const max = Math.max(...tools.map((t) => t.count), 1);
  $("#tools").innerHTML = tools
    .map(
      (t) => `<div class="bar-row" title="${esc(t.name)}: ${t.count} calls, p95 ${t.p95_ms ?? "–"}ms, ${t.errors} errors">
        <span class="name">${esc(t.name)}</span>
        <span class="track"><span class="fill" style="width:${((t.count / max) * 100).toFixed(1)}%"></span></span>
        <span class="val">${fmt(t.count)}</span>
      </div>`
    )
    .join("");
}

function sortSessions() {
  const { key, dir } = state.sort;
  const val = (s) => {
    switch (key) {
      case "fresh": return fresh(s.tokens);
      case "cache": return cacheRate(s.tokens);
      case "title": return s.title.toLowerCase();
      case "agent": return s.agent.toLowerCase();
      case "model": return s.model.toLowerCase();
      default: return s[key] ?? 0;
    }
  };
  state.sessions.sort((a, b) => {
    const va = val(a), vb = val(b);
    if (typeof va === "string") return va.localeCompare(vb) * dir;
    return (va - vb) * dir;
  });
}

function renderSessions() {
  sortSessions();
  const body = $("#sessions tbody");
  $("#session-count").textContent = `${state.sessions.length} in this project`;

  if (!state.sessions.length) {
    body.innerHTML = `<tr><td colspan="7"><div class="empty">No sessions recorded for this directory yet.</div></td></tr>`;
    return;
  }

  body.innerHTML = state.sessions
    .map((s) => {
      const errs = s.tool_errors ? `<span class="tag err">${s.tool_errors} err</span>` : "";
      return `<tr data-id="${esc(s.id)}" tabindex="0">
        <td>
          <div class="cell-title">
            <span class="t" title="${esc(s.title)}">${esc(s.title)}</span>
            ${s.sub ? '<span class="tag sub">sub</span>' : ""}
            ${errs}
          </div>
        </td>
        <td class="mono">${esc(s.agent)}</td>
        <td class="mono">${esc(s.model.split("/").pop())}</td>
        <td class="num mono">${fmt(s.tool_calls)}</td>
        <td class="num mono">${fmt(fresh(s.tokens))}</td>
        <td class="num mono">${(cacheRate(s.tokens) * 100).toFixed(0)}%</td>
        <td class="num mono">${ago(s.updated)}</td>
      </tr>`;
    })
    .join("");

  body.querySelectorAll("tr").forEach((tr) => {
    if (!tr.dataset.id) return;
    const open = () => openDrawer(tr.dataset.id);
    tr.addEventListener("click", open);
    tr.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); }
    });
  });
}

function renderLive() {
  const cur = state.overview?.current;
  const live = $("#live-state");
  if (!cur) {
    $("#live-meta").innerHTML = "";
    $("#live-steps").innerHTML = `<div class="empty">No session in this project.</div>`;
    live.textContent = "idle";
    return;
  }
  const s = state.sessions.find((x) => x.id === cur.id) || state.sessions[0];
  if (!s) return;

  const idleMs = Date.now() - s.updated;
  live.textContent = idleMs < 60_000 ? "active now" : "idle " + ago(s.updated).replace(" ago", "");

  $("#live-meta").innerHTML = `
    <div><span class="k">session</span><span class="v">${esc(s.title.slice(0, 30))}</span></div>
    <div><span class="k">agent</span><span class="v">${esc(s.agent)}</span></div>
    <div><span class="k">model</span><span class="v">${esc(s.model.split("/").pop())}</span></div>
    <div><span class="k">duration</span><span class="v">${span(s.updated - s.created)}</span></div>
    <div><span class="k">tokens</span><span class="v">${fmt(fresh(s.tokens))}</span></div>
    <div><span class="k">tools</span><span class="v">${fmt(s.tool_calls)}</span></div>`;

  loadSteps(s.id, $("#live-steps"), 10);
}

async function loadSteps(id, target, limit) {
  try {
    const data = await getJSON("/api/session?id=" + encodeURIComponent(id));
    const steps = data.steps.slice(-limit).reverse();
    if (!steps.length) {
      target.innerHTML = `<div class="empty">No tool calls in this session.</div>`;
      return;
    }
    target.innerHTML = steps
      .map(
        (st) => `<div class="step ${st.status === "error" ? "error" : ""}">
          <span class="status-dot"></span>
          <span class="tool">${esc(st.tool)}</span>
          <span class="hint" title="${esc(st.hint)}">${esc(st.hint) || "–"}</span>
          <span class="dur">${dur(st.duration_ms)}</span>
        </div>`
      )
      .join("");
  } catch (err) {
    target.innerHTML = `<div class="empty">${esc(err.message)}</div>`;
  }
}

async function openDrawer(id) {
  const drawer = $("#drawer");
  drawer.hidden = false;
  $("#drawer-title").textContent = "Loading…";
  $("#drawer-body").innerHTML = "";

  try {
    const d = await getJSON("/api/session?id=" + encodeURIComponent(id));
    $("#drawer-title").textContent = d.title;
    const toolList = Object.entries(d.tools)
      .sort((a, b) => b[1] - a[1])
      .map(([k, v]) => `${k} ×${v}`)
      .join(", ") || "none";

    $("#drawer-body").innerHTML = `
      <div class="kv">
        <span class="k">session id</span><span class="v">${esc(d.id)}</span>
        <span class="k">agent / model</span><span class="v">${esc(d.agent)} · ${esc(d.model)}</span>
        <span class="k">started</span><span class="v">${new Date(d.created).toLocaleString()}</span>
        <span class="k">duration</span><span class="v">${span(d.updated - d.created)}</span>
        <span class="k">assistant turns</span><span class="v">${d.messages}</span>
        <span class="k">tokens in / out</span><span class="v">${fmt(d.tokens.input)} / ${fmt(d.tokens.output)}</span>
        <span class="k">reasoning</span><span class="v">${fmt(d.tokens.reasoning)}</span>
        <span class="k">cache read / write</span><span class="v">${fmt(d.tokens.cache_read)} / ${fmt(d.tokens.cache_write)}</span>
        <span class="k">tool calls</span><span class="v">${d.tool_calls} (${d.tool_errors} errors)</span>
        <span class="k">tool mix</span><span class="v">${esc(toolList)}</span>
      </div>
      <h2 style="margin-bottom:10px">Tool timeline</h2>
      <div class="steps" id="drawer-steps"></div>`;

    $("#drawer-steps").innerHTML = d.steps
      .slice()
      .reverse()
      .map(
        (st) => `<div class="step ${st.status === "error" ? "error" : ""}">
          <span class="status-dot"></span>
          <span class="tool">${esc(st.tool)}</span>
          <span class="hint" title="${esc(st.hint)}">${esc(st.hint) || "–"}</span>
          <span class="dur">${new Date(st.ts).toLocaleTimeString()} · ${dur(st.duration_ms)}</span>
        </div>`
      )
      .join("") || `<div class="empty">No tool calls recorded.</div>`;
  } catch (err) {
    $("#drawer-title").textContent = "Error";
    $("#drawer-body").innerHTML = `<div class="empty">${esc(err.message)}</div>`;
  }
}

function closeDrawer() {
  $("#drawer").hidden = true;
}

async function refresh() {
  try {
    const [overview, sessions, workflow] = await Promise.all([
      getJSON("/api/overview"),
      getJSON("/api/sessions"),
      getJSON("/api/workflow"),
    ]);
    state.overview = overview;
    state.sessions = sessions;
    state.workflow = workflow;

    renderPipeline();
    renderStats();
    renderPortfolios();
    renderChart();
    renderTools();
    renderSessions();
    renderLive();

    setLive(true, `${overview.scope.name} · ${sessions.length} session(s)`);
    $("#updated").textContent = "updated " + new Date(overview.generated_at).toLocaleTimeString();
  } catch (err) {
    setLive(false, "db unavailable");
    toast("Cannot read data: " + err.message);
  }
}

function schedule() {
  clearInterval(state.timer);
  if ($("#auto").checked) state.timer = setInterval(refresh, 5000);
}

document.addEventListener("DOMContentLoaded", () => {
  $("#refresh").addEventListener("click", refresh);
  $("#auto").addEventListener("change", schedule);
  $("#drawer-close").addEventListener("click", closeDrawer);
  $("#drawer").addEventListener("click", (e) => {
    if (e.target.id === "drawer") closeDrawer();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeDrawer();
  });

  document.querySelectorAll("#metric-switch button").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("#metric-switch button").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      state.metric = btn.dataset.metric;
      renderChart();
    });
  });

  document.querySelectorAll("thead th[data-sort]").forEach((th) => {
    th.addEventListener("click", () => {
      const key = th.dataset.sort;
      state.sort = { key, dir: state.sort.key === key ? -state.sort.dir : -1 };
      renderSessions();
    });
  });

  refresh();
  schedule();
});
