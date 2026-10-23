---
description: Switch the output language (default English)
---

Target: `$ARGUMENTS` - one of `en` (English), `id` (Indonesian), or empty to show the current setting.

1. Read `.claude/config/lang.md`.
2. Map: `en` -> `English`, `id` -> `Indonesian`. If empty, reply with the current language and stop.
3. Replace the `Output language:` line with the mapped value. Change nothing else in the file.
4. Reply in one line: `Language set to <English|Indonesian>. Future documents and replies use this language.`

Do not translate existing files, do not rewrite skill modules, do not regenerate portfolios.
