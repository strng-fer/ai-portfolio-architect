# References Study

Mined with `mine_github.py --query "llm agent workflow" --limit 8` and `ref_digest.py --query "llm agent tool budget"`. The arXiv export API returned HTTP 429 for every retry, so the two papers were resolved through the Hugging Face papers index and cite real arXiv ids.

## Repositories
| Name | Why relevant | Part to study |
|---|---|---|
| openai/openai-agents-python | Minimal agent runtime: turn limits, guardrails, and a runner loop close to the one this blueprint writes explicitly | How the runner counts turns and what happens at the limit |
| deepset-ai/haystack | Retrieval pipelines exposed as tools, the same seam this project needs between retrieval and the tool registry | Retriever and tool component contracts |
| comet-ml/opik | Tracing and evaluation for agent runs, a reference for the step-level trace schema and per-step cost | Trace record shape and eval scoring |

## Papers
| Title | Idea adopted | Part to study |
|---|---|---|
| ToolScope (2026, arXiv 2510.20036) | Tool-set size and description length degrade selection accuracy and eat context, so the tool set stays at three and each tool carries a short description | Tool-selection accuracy measurement design |
| MCPToolBench++ (2025, arXiv 2508.07575) | Real-world tool success is not guaranteed and the context window caps how many tools one run can call, which justifies a per-run call cap | Multi-step call accounting and failure taxonomy |

## Takeaway
The repos supply the loop and trace vocabulary; the papers supply the argument that a call cap is a correctness feature, not an optimisation. Nothing here is copied: the ledger and the stop rule are the parts this project adds.
