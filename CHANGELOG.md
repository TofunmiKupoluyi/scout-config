# Changelog

## 2026-11-04b — Judge's placebo and plateau repaired (NOS-44)
- Judge's placebo now relabels the ranking within the names your config actually ranks, keeping the book's shape; the old whole-column shuffle built mis-shaped books that bled through the risk framework and failed NOS-29, NOS-64 and NOS-126 on a negative placebo. The plateau line runs the chosen point's neighbours when the sweep sample holds none instead of passing vacuously.
- New For Scout phrase `placebo control off` (`research-scout` skill, `TICKET_FORMAT.md` synced from judge-config): the construction, not your proposal — do not redesign around it.

## 2026-11-04 — hourly resolution (schema 1.1)
- `trade-config-spec` §2b: `schedule.resolution: "1h"` runs a config on an hourly grid — hour-of-day, session, hour-to-hour and intraday-flow ideas are now proposals, not data requests. Bar fields are the hour's bar, `hour_utc`/`dow` stamp the row, windows count hours, schedule keys `rebalance_hours`, `holding_hours`, `delay_hours`. New daily field `dow`. Minute-scale ideas remain data requests.
- `validate_config.py` and `TRADE_CONFIG_SCHEMA.json` synced from judge-config; new `examples/example_hour_of_day.json`; `ALPHA_SOURCES.md` no longer sends intraday ideas to daily aggregates only.
- Judge's placebo line is now scored gross of costs (bar version 2026-11-04), so "fails the placebo" no longer appears just because a construction trades a lot.

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
