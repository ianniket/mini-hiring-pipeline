# Mini Hiring Pipeline - Submission

**GitHub Repository Link:** [https://github.com/ianniket/mini-hiring-pipeline](https://github.com/ianniket/mini-hiring-pipeline)

---

### App Design & UI

*(Please paste a screenshot of the main Kanban board here)*



---

### Audit History Modal

*(Please paste a screenshot of a candidate's Audit History open here)*



---

### Decisions Made
* **SQLite Database:** Selected for simplicity and speed of development, providing a robust relational schema for the audit trail.
* **FastAPI:** Chosen to quickly build REST APIs with built-in validation via Pydantic.
* **Vanilla CSS (Glassmorphism):** Used over Tailwind to manually craft a highly customized, premium UI without a large dependency footprint.
* **Custom NLP Heuristics:** Instead of relying on an external LLM (which introduces latency), the search query logic uses custom algorithms (Levenshtein distance) and regex.
* **Audit Trail Immutability:** Implemented by enforcing that history records are append-only. Stages can only move forward chronologically.
