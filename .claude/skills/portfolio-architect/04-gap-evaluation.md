# Job Fit & Portfolio Leverage Scoring Rubric

Use these weights (100 points total) when scoring jobs in `/scrape` and `/rank`:

1. **Skill-Bridge Ratio (40 points)**:
   - Full score (35-40) when the candidate already covers 50-75% of the posting's stack, so the remaining 25-50% can be learned by building this project.
   - Deduct points when the posting is 100% too easy (nothing new to learn) or 100% out of reach (needs more than 6 months of fundamentals).
2. **Engineering Problem Clarity (30 points)**:
   - High score when the posting names specific technical challenges (scalability, data integration, AI pipelines, reliability).
3. **Reusability & Market Demand (30 points)**:
   - High score when the resulting stack and architecture also apply to many similar companies.

Report the score plus a <=12-word idea per job. No narrative.
