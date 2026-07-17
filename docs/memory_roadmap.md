# Pie Agent Memory Roadmap

## Phase 1: Markdown Memory

Use a local `MemoryTool` and human-readable Markdown files:

- `memory/conversation.md` holds a bounded, chronological user/assistant transcript.
- `memory/facts.md` holds durable facts saved only when the user explicitly says
  `remember ...` or `remember that ...`.
- Load the five newest conversation exchanges and all saved facts before each
  LLM request.
- Build prompts in this order: agent instructions, remembered user data, recent
  conversation, then the current user request.
- Mark loaded facts and history as user data rather than instructions, so they
  cannot override the agent's safety rules.
- Append each completed exchange to the transcript and trim older exchanges.
- Keep `memory/` out of Git because it can contain personal information.

Phase 1 deliberately does not infer user facts or provide deletion commands.
Users can inspect and edit the Markdown files directly.

## Phase 2: Mature Local Memory

Migrate/import the Markdown data into a versioned local SQLite database and add:

- Local Ollama embeddings for semantic retrieval of relevant facts, summaries,
  and past exchanges.
- Periodic conversation summaries while retaining recent raw exchanges.
- Metadata such as timestamps, source, confidence, last-used time, retention,
  expiry, and duplicate detection.
- User controls to list, correct, delete, export, import, clear, or disable
  memory.
- Database migrations, backups, relevance limits, and prompt-size limits.
- Tests for semantic ranking, summaries, migration/import, expiry,
  disabled-memory behavior, backups, and prompt-injection resistance.
