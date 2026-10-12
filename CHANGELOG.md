# Changelog

## 2026-10-12 — redesign v2: hypothesis → framework → config
- Scout's output is now three things: a one-line alpha hypothesis, a plain-words trade framework, and a declarative trade config (schema 1.0) that Judge's engine runs unchanged. Scout no longer writes `signal.py`, feature definitions against a panel API, or proposal JSON with scores.
- Scout no longer carries the backtest or risk side: `reference/RISK_FRAMEWORK.*`, `reference/REJECTION_PATTERNS.md` (gate numbers) and the `data-and-backtest` skill are removed; `reference/WHAT_FAILED_BEFORE.md` keeps the inherited record in plain words.
- One Linear issue per experiment, four statuses (Idea Generated, Critiqued, Discarded, Human Review), up to five framework rounds as `[SCOUT FRAMEWORK n/5]` comments; layout in `reference/TICKET_FORMAT.md`.
- New `trade-config-spec` skill (fields, ops, schema, ranges, validation, examples), `tools/validate_config.py`, `reference/TRADE_CONFIG_SCHEMA.json`, `examples/`.
- `AGENTS.md`, `research-scout` skill, `ALPHA_SOURCES.md` conventions and README rewritten for the new flow. Linear tool protocol unchanged.
