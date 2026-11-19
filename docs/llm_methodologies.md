# CampusFlow AI – LLM Methodologies

## 1. Foundation Model Strategy: Pre-Training vs Fine-Tuning
CampusFlow AI leverages a pretrained foundation model (**Google Gemini 3.5 Flash-Lite**, exact identifier: `gemini-3.5-flash-lite`, accessed via the modern `google-genai` Python SDK).

> [!NOTE]
> **Engineering Integrity Note:** CampusFlow AI does **NOT** pre-train a foundational language model from scratch (which requires millions of dollars in compute) nor does it perform parameter-efficient fine-tuning (PEFT/LoRA). Doing so would risk catastrophic forgetting of general reasoning and date parsing capabilities. Instead, CampusFlow AI implements three advanced production-grade methodologies:
> 1. **Few-Shot & System Prompt Engineering**
> 2. **Retrieval-Augmented Generation (RAG)**
> 3. **Executable Multi-Layer Guardrails**

---

## 2. Prompt Engineering Methodology
Implemented in `backend/app/services/prompt_service.py` and `gemini_service.py`:
- **Role Definition:** Configures the LLM as an expert academic information extraction assistant.
- **Strict Formatting & JSON Mode:** Utilizes `response_mime_type="application/json"` with explicit Pydantic schema validation.
- **Temporal Anchoring:** Injects dynamic reference dates (`Reference Today's Date: YYYY-MM-DD (Day)`) into the system prompt to resolve calendar offsets accurately.
- **Date Grounding & Anti-Hallucination Constraints:** Direct instructions explicitly prohibiting the model from inventing dates or confusing submission deadlines with examination dates.
- **Ambiguity Detection Prompts:** Dedicated templates prompting the model to flag relative phrases ("next Monday", "by tomorrow") for human-in-the-loop verification.

---

## 3. Retrieval-Augmented Generation (RAG) Methodology
Implemented in `backend/app/services/rag_service.py` and `backend/app/routers/rag.py`:
- **Vector Database:** Persistent **ChromaDB** with cosine similarity distance metric.
- **Embedding Generation:** Sentence Transformers (`all-MiniLM-L6-v2`) via ONNX runtime for sub-second embedding generation.
- **Context Chunking:** Page-aware text chunking that retains `page_number`, `document_name`, and `user_id`.
- **User-Level Metadata Isolation:** Every query enforces `where={"user_id": str(user_id)}`, ensuring zero cross-tenant data leakage.
- **Context Augmentation:** When analyzing an announcement, previously indexed circulars, syllabi, and manuals are retrieved and injected as ground-truth reference context.
- **Source Attribution:** Extracted tasks link back to specific source document chunks and page numbers.

---

## 4. Guardrail Methodologies
Implemented in `backend/app/services/guardrail_service.py`:
- **Layer 1: Input Guardrails:** Restricts file extensions (.pdf, .png, .jpg), caps file size (15MB), sanitizes input, and filters prompt-injection attacks.
- **Layer 2: LLM Output Guardrails:** Pydantic schema validation, date ISO normalization, category validation, and event vs deadline separation.
- **Layer 3: Human-in-the-Loop Guardrails:** Extracted tasks require explicit student review, edit, or confirmation before persisting to PostgreSQL.
- **Layer 4: Scheduling Guardrails:** Enforces hard constraints: no session scheduled after deadlines, no session during college hours, minimum 15-minute breaks, and rejection of impossible workloads.
