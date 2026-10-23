#!/usr/bin/env bash
set -e

echo "[*] Preparing links for AI CLIs ([CC], OpenCode, Aider, Gemini CLI)..."

# 1. Mirror CLAUDE.md to AGENTS.md (OpenCode and modern AI CLIs read AGENTS.md).
#    Copy is the default: it works on every filesystem, including Windows without
#    developer mode. Symlinks confuse some Windows checkouts and CI runners.
cp CLAUDE.md AGENTS.md
echo "[i] AGENTS.md copied from CLAUDE.md"

# 2. Mirror .claude/commands to .opencode/command so slash commands work in OpenCode.
mkdir -p .opencode
rm -rf .opencode/command
mkdir -p .opencode/command
cp .claude/commands/*.md .opencode/command/

# 3. Make every Python script executable.
chmod +x tools/*.py .agents/skills/*/*.py

# 4. Ensure the output language config exists (English by default).
if [ ! -f .claude/config/lang.md ]; then
  mkdir -p .claude/config
  printf '# Output Language\n\nOutput language: English\n' > .claude/config/lang.md
  echo "[i] Created .claude/config/lang.md (English)"
fi

echo "[+] Done. Commands ready: /setup /scrape /rank /applyidea /prompt /scaffold /lang /expand /reset"
