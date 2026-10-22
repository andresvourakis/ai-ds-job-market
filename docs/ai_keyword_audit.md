# AI keyword audit

How the AI keywords on the AI in Data Science page were validated, and the one rule that came out of it.

**Re-run any check with:**

    poetry run python audit_ai_keywords.py "<canonical name>" --samples 20
    poetry run python audit_ai_keywords.py "<canonical name>" --rejected --samples 20   # what a context rule drops

**Method:**
- Read a random sample of real matched snippets for each keyword, taken from the deduplicated Data Scientist postings.
- Judge whether each match means what the keyword claims.
- Keep keywords at roughly 90% precision or better, the same bar as `production_keyword_audit.md`.

**Audit details:** run on 2026-10-20, on 7,756 deduplicated postings. 20 matches were sampled per keyword.

## Kept as is (precision at or above the bar)

- **100% precision:** LLMs, GenAI, NLP, RAG, AI Agents, Prompt Engineering, LangChain, LangGraph, Embeddings, Hugging Face, Foundation Models, Anthropic, MCP, Ontology, Claude Code, Semantic Search, Context Engineering, LlamaIndex, AI Workflow, Pinecone, ChatGPT, RLHF, Codex, A2A, LoRA, ADK, AutoML, Weaviate, Chroma, sLMs, Vector Database.
- **Anthropic:** almost all matches are the word "Claude". All 20 meant the model, and no person named Claude turned up.
- **Fine-tuning:** 17 of 19. Misses are "fine tuning parameters/prompts". Kept, but watch it.
- **Semantic Layer:** 14 of 19. "Semantic modeling" sometimes means knowledge graphs. It counts toward the AI headline, but it rarely is the only AI skill in a posting.

## Context rule: Orchestration, Guardrails, Tracing

Bare, these are ordinary words. Without a rule, their precision was:

| Word | Precision without a rule | What the misses were |
|---|---|---|
| orchestration | 10 of 20 | Airflow, dbt, Dagster and Kubernetes orchestration |
| tracing | 12 of 20 | Data lineage, blockchain forensics, SRE distributed tracing, "tracing its roots" |
| guardrails | 16 of 20 | Experiment guardrail metrics, compliance guardrails |

Every correct match had an unambiguous AI term nearby. So `CONTEXT_RULES` in `analyse_job_market.py` counts a bare form only when a support term appears within `CONTEXT_WINDOW` (100) characters.

**Support terms:**
- **orchestration:** `AI_SUPPORT_TERMS`, i.e. LLM, large language model, agent(s), agentic, GenAI / gen AI / generative AI, foundation model, RAG, LangChain, LangGraph, Langfuse, LangSmith, LLMOps.
  - Deliberately excluded: "tool", "prompt", "model" and a bare "AI". "AI/ML pipeline orchestration" is still Airflow.
- **guardrails, tracing:** `AI_SAFETY_TERMS`, which is the list above plus a bare "AI", artificial intelligence, responsible AI / RAI, hallucination(s), OpenAI, Anthropic, Claude, GPT, jailbreak(s).
  - The audit of dropped matches found real AI guardrails phrased as "AI driven products ... safety guardrails" and "Anthropic, Azure OpenAI ... guardrails". Experiment guardrails had none of these terms nearby.

Qualified variants ("LLM Orchestration", "AI Guardrails", "LLM Guardrails", "LLM Tracing") are longer forms and always count.

**Result after the rule** (both directions audited):

| Word | Postings counted | Kept matches about AI | Dropped matches not about AI |
|---|---|---|---|
| Orchestration | 269 | 19 of 20 | 19 of 20 |
| Guardrails | 112 | 20 of 20 | about 16 of 20 (a few real AI guardrails lost, slightly conservative) |
| Tracing | 12 | 12 of 12 | 10 of 10 |

**Effect on the headline** ("postings naming a specific AI skill", 2026-10-20 data):
- It falls from 46.1% to 44.1%.
- Removing the three words entirely would give 44.0%. When they are about AI, the posting nearly always names another AI skill as well.

## Known gaps (not fixed)

- **Spellings the keyword list misses:** "Gen AI" with a space, "computer vision", "object detection" and "OCR". These are about 1 in 10 of the postings whose only match is a bare "AI".
- **"AI agents" covers only three phrases:** "AI agents", "LLM agents" and "agentic AI". It misses "agentic workflows", "multi-agent" and "build agents". A broad phrase set finds AI agent language in 15% of postings, against 9% for the keyword.
- **BI tools named with ordinary words** (not an AI keyword):
  - "Evidence" was 0 of 20 correct.
  - "Mode" was 5 of 20; most misses are one template line, "multi mode communications".
  - "Omni" was 12 of 20; the misses are "omni channel".
