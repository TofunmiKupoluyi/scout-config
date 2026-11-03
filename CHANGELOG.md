# Changelog

## 2026-11-03 — session id on every research write
- Every POST/PUT/PATCH to the research API sends `X-Session-Id: <your session id>` (from the system prompt); a write without it is a 400. The store records it as provenance (who filed or closed an idea, who requested or resolved a data source, who indexed a paper), so each row links back to its run.

## 2026-11-03 — trade-size taker flow fields (NOS-102)
- Six daily fields from the bucket's `taker_flow` dataset (aggTrades): `taker_net_usd`, `taker_gross_usd` (all prints), `taker_net_small_usd`, `taker_gross_small_usd` (prints under $1k), `taker_net_large_usd`, `taker_gross_large_usd` (prints of $100k and over). Day t−1's dollars stamped at t, never forward-filled (NaN on a missing day). `trade-config-spec` documents them with the print-is-not-a-parent-order caveat; `validate_config.py` synced from judge-config; `ALPHA_SOURCES.md` no longer says the size split waits on data.

## 2026-11-03 — claims and ideas replace the idea map
- `reference/IDEA_MAP.json` is deleted, not imported: its 31 cells were broad parents of the ideas Linear already holds, and their scores, `next_test` and `ledger_refs` were hand-guessed or duplicated Linear.
- The context pack reads the research API instead (`reference/RESEARCH_API.md`): the claim frontier (`GET /claims?grounded=false&testable=true`) and the ideas already tried (`GET /ideas`, with findings). Dedup is `GET /ideas?q=` across every status.
- Every experiment is also filed as an idea (`POST /ideas`, grounded in testable claims, cited in the ticket); Scout's own Discards record their finding (`PATCH /ideas/<identifier>`).
- Missing data is a REQUESTED data source (link or `POST /data-sources`), no longer an escalation. Escalations remain for data defects, disputed Judge results and §2 conflicts.
- `ALPHA_SOURCES.md` keeps its eight families and the inherited record as prose; the families are no longer labels. `TICKET_FORMAT.md` cites claims and related ideas (synced to judge-config).

## 2026-10-12 — redesign v2: hypothesis → framework → config
- Scout's output is now three things: a one-line alpha hypothesis, a plain-words trade framework, and a declarative trade config (schema 1.0) that Judge's engine runs unchanged. Scout no longer writes `signal.py`, feature definitions against a panel API, or proposal JSON with scores.
- Scout no longer carries the backtest or risk side: `reference/RISK_FRAMEWORK.*`, `reference/REJECTION_PATTERNS.md` (gate numbers) and the `data-and-backtest` skill are removed; `reference/WHAT_FAILED_BEFORE.md` keeps the inherited record in plain words.
- One Linear issue per experiment, four statuses (Idea Generated, Critiqued, Discarded, Human Review), up to five framework rounds as `[SCOUT FRAMEWORK n/5]` comments; layout in `reference/TICKET_FORMAT.md`.
- New `trade-config-spec` skill (fields, ops, schema, ranges, validation, examples), `tools/validate_config.py`, `reference/TRADE_CONFIG_SCHEMA.json`, `examples/`.
- `AGENTS.md`, `research-scout` skill, `ALPHA_SOURCES.md` conventions and README rewritten for the new flow. Linear tool protocol unchanged.
