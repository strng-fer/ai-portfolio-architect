# Role Pack

<!-- Single source of truth for the active domain pack. Agents read the line below. -->

Active pack: llm

<!-- Usage -->
Pack: one file name from `.claude/packs/` without the extension.
Change with `/setup` (it picks by target role) or set it by hand.
List available packs: `python tools/pack_load.py --list`
Inspect the active pack: `python tools/pack_load.py --name llm`

The pack supplies the metric families, banned idea shapes, default mechanisms, and
reference-source policy for this candidate's domain. It does not change the file
layout or the word budgets.
