# References Study

## Repositories

| Name | Why relevant | Part to study |
|---|---|---|
| [noyce6983981-max/ocr-vlm-local-retrieval](https://github.com/noyce6983981-max/ocr-vlm-local-retrieval) | Local-first OCR plus vision-language retrieval with an independent evaluation harness; closest match to the cascade design | How it separates extraction from evaluation, and where it stores region metadata |
| [nvtanphat/NoelysRAG](https://github.com/nvtanphat/NoelysRAG) | Evidence-preserving multimodal RAG using hybrid dense plus sparse retrieval | The evidence-preservation contract: how a retrieved chunk stays tied to its source page |
| [nannib/RAGForge](https://github.com/nannib/RAGForge) | Multimodal extraction and normalization pipeline covering OCR, captions, and document text | Normalization rules that make cross-engine text comparable |

## Papers

| Title | Idea adopted | Part to study |
|---|---|---|
| [Scaling Beyond Context: A Survey of Multimodal RAG for Document Understanding](http://arxiv.org/abs/2510.15253v3) | Taxonomy of OCR-based versus vision-native document pipelines, used to justify the cascade over a single vision call | Comparison criteria for pipeline families and their reported failure modes |
| [From Pixels to Structure: Lightweight VLMs for Document OCR and Structured JSON Extraction](http://arxiv.org/abs/2610.11818v1) | Evidence that small vision models can carry structured extraction without commercial APIs, supporting the CPU and free-tier constraint | Evaluation protocol for structured output and its handling of malformed fields |

## Notes

- The survey supplies the argument for keeping a deterministic verifier outside the model; the second paper supplies the evaluation protocol shape (field-level match rather than token overlap).
- No reference is used for span verification itself; that mechanism is built from geometry overlap and fuzzy span matching, and is the original contribution of this project.
