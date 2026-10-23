# Language Policy

Two languages, one source of instructions. Do not duplicate files per language: duplicates double maintenance and double the tokens an agent must read.

## 1. Instruction language: English (fixed)
Everything inside `.claude/`, `.agents/`, and `tools/` is written in English. This is canonical. Agents never need to translate instructions to understand them.

## 2. Output language: configurable
Read the `Output language:` line in `.claude/config/lang.md`.

- `English` (default) - every generated document, table, heading, diagram label, and chat reply uses English.
- `Indonesian` - same artifacts in Indonesian.

Applied to:
- `00_job_analysis.md` ... `05_agent_prompts.md`
- `Blueprint_Final.md` / `.pdf`
- Mermaid diagram labels
- Chat status lines and the final summary
- `portfolio_tracker.csv` free-text columns (project title only; headers stay English)

Not translated:
- File names, folder slugs, CSV headers, code identifiers, commit messages, and this repository's own source files.
- Skill modules, commands, and tool output.

## 3. Chat language
Reply in the language the user writes in. If the user writes Indonesian while output language is English, reply in Indonesian but keep documents in English. The config controls documents, not conversation.

## 4. Switching
`/lang en` or `/lang id`. One line changed in the config file. Existing portfolios keep their original language; do not retro-translate them unless asked.

## 5. Mixed-language safety
- Never mix languages inside one document. Pick one per artifact.
- Keep technical terms untranslated (e.g. *idempotency*, *backpressure*, *recall@k*, `pgvector`) in both languages.
- Diagram node IDs stay ASCII. Labels follow output language.
- If output language is unknown or the config is unreadable, default to English and continue without asking.

## 6. Localized user docs
`README.md` = English (default). `README.id.md` = Indonesian. Keep both in sync when commands or file layouts change.
