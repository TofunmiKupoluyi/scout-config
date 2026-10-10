# scout-config

Configuration for **Scout**, agent A of a two-agent alpha-research desk on Binance USDT-M perpetual futures (market-neutral, cross-sectional). Scout runs as fresh-context sessions of two kinds. A **fresh run** (no ticket attached) posts exactly three new research ideas as Linear tickets and updates its journal. A **ticket run** reads the ticket's status and comment thread and acts only when it is Scout's turn — today that is exactly one status: Critiqued → answer the critique and post the `PREREG`, set Pre-registered; any other status ends the run. Each ticket is picked up by a **Judge** (its own config, not in this repo); the ticket's status is the whole state machine, which also makes runs idempotent — a stray or duplicate trigger finds nothing that is Scout's turn and ends. Later pipeline stages (gate, build, battery, verdict) get statuses and actions when they are wired. Every research record lives in Linear (team **NoSyntax**), never in this repo or on the filesystem — see `AGENTS.md` §0; Linear is Scout's only memory between runs.

## Layout

| Path | What it is |
|---|---|
| `AGENTS.md` | Scout's master prompt. §0 is the Linear protocol (the system of record), §4 the run procedure, §9 the three human decisions. |
| `reference/RISK_FRAMEWORK.md` / `.json` | The production risk model, binding on proposals (universe, caps, sizing, governor; §14 is the Scout-facing summary). The `.json` is the machine-readable twin. |
| `reference/REJECTION_PATTERNS.md` | The five ways 140+ past tests failed; every proposal must say why it is not one of them. |
| `reference/GLOSSARY.md` | Human names for the production sleeves and sizing vocabulary (`a4` FundingCarry, `a12` IlliquidityPremium, `a90x_ratio` TakerFlow-R, …). |
| `.agents/skills/research-scout/` | Scout's task skill: proposal schema, signal contract, build checklist, idea-map hygiene. |
| `.agents/skills/data-and-backtest/` | Data model, the panel contract feature definitions are written against, point-in-time rules, the battery's target/windows/gates K1–K5, the adoption bar. |
| `.agents/skills/binance-futures-data/` | The S3 data bucket: candles, funding rates, open-interest metrics — layout, schemas, access, pitfalls. |
| `.claude/skills` | Symlink to `.agents/skills` so Claude Code discovers the skills. |

## What Scout touches, and what it never does

This is a config repo: it contains no executable research code, by design. Scout's whole surface is the Linear API (records), read-only S3 (the data bucket, for coverage and buildability checks), and local scratch.

Scout writes proposals and pre-registrations whose feature definitions target the panel contract in the `research-scout` skill. The build, battery and verdict stages are not wired yet; when they are, Judge executes the submitted code and posts the `VERDICT` — Scout never runs a backtest and never sees battery output, which is what keeps pre-registration honest.

Scout assembles its own context pack from Linear at the start of every run (idea map, ledger tail, coverage map, recent verdicts, open escalations, the experiment count N — the `research-scout` skill lists the queries), with the rejection patterns from `reference/` and the data catalogue from the S3 meta files plus the panel contract. There are no budget caps: the schedule is the budget (three ideas per run, at most one `PREREG` per critique cycle; cadence is a §9 human decision), and N is always reported with any winner. The only inputs that genuinely arrive with a run are an optional attribution report (autopsy) or a source to scout. Secrets are referenced by name only: `LINEAR_API_KEY`, `AWS_S3_ACCESS_KEY`, `AWS_S3_ACCESS_KEY_SECRET`.

Two pieces therefore live outside this repo and must exist for the loop to run end to end: the **triggers** — a schedule for fresh runs, and whatever starts a ticket run when a ticket turns Scout's way (a Linear webhook on status change, say) — and **Judge's battery** that supplies the `panel` object per the contract in `data-and-backtest`, executes submitted `signal.py`, and posts verdicts. The battery does not exist yet; the specs here are its blueprint. Before the first run: the standing Linear issue `Scout Journal` must be created, and three panel inputs are unprovisioned in the data itself (market cap, premium index, full symbol tags — see `data-and-backtest` §1).

All state — hypotheses, critiques, pre-registrations, the ledger, the idea map, the journal, escalations — lives in Linear per `AGENTS.md` §0.
