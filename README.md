# scout-config

Configuration for **Scout**, agent A of a two-agent alpha-research desk on Binance USDT-M perpetual futures (market-neutral, cross-sectional). The partner agent, **Judge**, has its own config (not in this repo). Scout's behaviour is defined entirely by the files here; every research record lives in Linear (team **NoSyntax**), never in this repo or on the filesystem — see `AGENTS.md` §0.

## Layout

| Path | What it is |
|---|---|
| `AGENTS.md` | Scout's master prompt. §0 is the Linear protocol (the system of record), §4 the task loop, §9 the three human decisions. |
| `reference/RISK_FRAMEWORK.md` / `.json` | The production risk model, binding on proposals (universe, caps, sizing, governor; §14 is the Scout-facing summary). The `.json` is the machine-readable twin. |
| `reference/REJECTION_PATTERNS.md` | The five ways 140+ past tests failed; every proposal must say why it is not one of them. |
| `reference/GLOSSARY.md` | Human names for the production sleeves and sizing vocabulary (`a4` FundingCarry, `a12` IlliquidityPremium, `a90x_ratio` TakerFlow-R, …). |
| `.agents/skills/research-scout/` | Scout's task skill: proposal schema, signal contract, build checklist, idea-map hygiene. |
| `.agents/skills/data-and-backtest/` | Data model, derived panels, point-in-time rules, the battery's target/windows/gates K1–K5, the replica simulation. |
| `.agents/skills/binance-futures-data/` | The S3 data bucket: candles, funding rates, open-interest metrics — layout, schemas, access, pitfalls. |
| `.claude/skills` | Symlink to `.agents/skills` so Claude Code discovers the skills. |

## What Scout touches, and what it never does

This is a config repo: it contains no executable research code, by design. Scout's whole surface is the Linear API (records), read-only S3 (the data bucket, for coverage and buildability checks), and local scratch while drafting `signal.py`.

Scout **writes** `signal.py` against the panel interface documented in the `research-scout` skill but **never executes** it, the battery, or any backtest: Judge runs the fixed battery on the submitted code and posts the `VERDICT` on the hypothesis issue. Scout never sees battery output, which is what keeps pre-registration honest.

Delivered with each task, not stored anywhere: the context pack (idea map, ledger tail, coverage map, data catalogue, recent verdicts, open escalations), budget facts, the slot type, the `<ID>` for a build, and attribution reports for AUTOPSY. Secrets are referenced by name only: `LINEAR_API_KEY`, `AWS_S3_ACCESS_KEY`, `AWS_S3_ACCESS_KEY_SECRET`.

All state — hypotheses, pre-registrations, builds, verdicts, the ledger, the idea map, the journal, escalations — lives in Linear per `AGENTS.md` §0.
