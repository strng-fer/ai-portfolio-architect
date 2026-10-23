#!/usr/bin/env bash
set -e

echo "[*] Menyiapkan symlink lintas AI CLI (Claude Code, OpenCode, Aider, Gemini CLI)..."

# 1. Symlink CLAUDE.md ke AGENTS.md (Standar OpenCode & AI CLI modern)
ln -sf CLAUDE.md AGENTS.md

# 2. Symlink folder .claude/commands ke .opencode/command agar /setup, /scrape, /applyidea berjalan di OpenCode
mkdir -p .opencode
rm -rf .opencode/command
ln -sf ../.claude/commands .opencode/command

# 3. Berikan izin eksekusi pada semua script Python
chmod +x tools/*.py .agents/skills/*/*.py

echo "[+] Setup selesai! Semua command (/setup, /scrape, /applyidea, /rank, /scaffold) siap digunakan."
