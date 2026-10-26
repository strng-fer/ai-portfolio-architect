# Job Fit & Portfolio Leverage Scoring Rubric

Use these weights (100 points total) when scoring jobs in `/scrape` and `/rank`:

1. **Skill-Bridge Ratio (40 points)**:
   - Score from the evidence ledger, not from the profile narrative. Run `python3 tools/skill_evidence.py gap --needs "<posting stack>"` and use its counts.
   - Full score (35-40) when the candidate already covers 50-75% of the posting's stack (`solid` + `thin` rows dominate), so the remaining 25-50% can be learned by building this project.
   - Deduct points when the posting is 100% too easy (`solid` everywhere, nothing new to learn) or 100% out of reach (`missing` exceeds the ceiling of 2, needs more than 6 months of fundamentals).
   - The `missing` list is the project's new-technology axis. A posting with zero `missing` skills needs a harder mechanism, not a new stack.
2. **Engineering Problem Clarity (30 points)**:
   - High score when the posting names specific technical challenges that map to a mechanism in `12-mechanism-catalogue.md` (scalability, data integration, AI pipelines, reliability, grounding, drift).
   - Low score when the responsibilities are generic ("build features", "collaborate with stakeholders") and no mechanism signal can be extracted.
3. **Reusability & Market Demand (30 points)**:
   - High score when the resulting stack and architecture also apply to many similar companies.
   - Prefer mechanisms that appear across domains over mechanisms tied to one employer's internal tool.
   - In product mode, subtract up to 10 points when no mechanism the posting suggests can serve an audience in `01c-product-intent.md`. A job that leads to a project nobody can use is a weaker investment, however good the CV line.

Report the score plus a <=12-word idea per job. The idea must name a mechanism, not a feature. No narrative.
