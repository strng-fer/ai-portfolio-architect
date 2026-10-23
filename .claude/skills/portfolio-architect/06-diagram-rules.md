# Mermaid Diagram Rules

Diagrams replace paragraphs. Keep them small so they render fast and stay readable in PDF.

## Size limits
- `system_architecture.mmd`: max **15 nodes**, max 2 levels of depth.
- `user_workflow.mmd`: max **6 actors/participants**, max 12 main messages.
- One diagram = one idea. Too much? Split it, do not stack nodes.

## Syntax
1. `flowchart TD` or `flowchart LR` for architecture; `sequenceDiagram` for flow.
2. Wrap labels containing parentheses, slashes, colons, or special characters in double quotes:
   - Correct: `A["FastAPI (API)"] --> B["PostgreSQL / pgvector"]`
   - Wrong: `A[FastAPI (API)] --> B[PostgreSQL / pgvector]`
3. No HTML tags (`<br/>`, `<b>`) inside `sequenceDiagram`.
4. Short node IDs (`A`, `B`, `C`), descriptive labels. No emoji.

## Label content
- Architecture: component + role (`"Queue (buffer)"`), not class names.
- Flow: human or system actors (`User`, `API`, `Worker`), messages as actions.
- Never put code, file paths, or function names in a diagram.
- Labels follow the configured output language. Node IDs stay ASCII.

## Three labels worth adding
- Mark trust boundaries: `"LLM (untrusted)"` vs `"Verifier (deterministic)"`.
- Mark failure points: `"Queue (retry + DLQ)"`.
- Mark decisions: `"Cache (hit/miss)"`.
Three extras are enough. Do not decorate every node.
