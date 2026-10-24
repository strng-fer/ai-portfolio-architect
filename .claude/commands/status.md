---
description: Show status of all portfolio folders and the next action for each
---

Target (optional): `$ARGUMENTS` - a portfolio slug or folder path. Empty means all.

Run `python3 tools/portfolio_status.py $ARGUMENTS`.

Then:
1. Print the script output as-is (it is already compact).
2. Add max 2 lines: the single most important next action, and any inconsistency between `portfolio_tracker.csv` and the files on disk.
3. If a portfolio is `INCOMPLETE`, name the exact missing file and the command that writes it.
4. If a portfolio is `UNTRACKED`, offer to either add a tracker row or remove the folder - do not decide silently.

Never open documents or PDFs to summarise them. Status comes from the script only.
