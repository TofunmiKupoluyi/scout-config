# scout-config

Configuration for **Scout**, agent A of a two-agent alpha-research desk on Binance USDT-M perpetual futures (market-neutral, cross-sectional). Scout runs as fresh-context sessions of two kinds. A **fresh run** (no ticket attached) posts exactly one new research idea as a Linear ticket — throughput is tuned by scheduling runs more often, not by batching ideas. A **ticket run** reads the ticket's status and comment thread and acts only when it is Scout's turn — today that is exactly one status: Critiqued → answer the critique, post the revised proposal JSON as a `REVISED PROPOSAL vN` comment, and set the ticket back to Idea Generated for Judge to re-review; any other status ends the run. Ticket runs arrive through the Linear webhook: creating an issue pins the creating conversation to it, so the issue's later events (critiques, status changes) land back in that conversation rather than starting a new session. The loop repeats until **Judge** (its own config, not in this repo) moves the ticket to Human Review or closes it — or Scout sets it to Discarded when a critique names a hard blocker it cannot fix. The ticket's status is the whole state machine, which also makes runs idempotent — a stray or duplicate trigger finds nothing that is Scout's turn and ends. Later pipeline stages (build, battery, verdict) get statuses and actions when they are wired. Every research record lives in Linear (team **NoSyntax**), never in this repo or on the filesystem — see `AGENTS.md` §0; Linear is Scout's only memory between runs.

## Layout

| Path | What it is |
|---|---|
| `AGENTS.md` | Scout's master prompt. §0 is the Linear protocol (the system of record), §4 the run procedure, §9 the three human decisions. |
| `reference/RISK_FRAMEWORK.md` / `.json` | The production risk model, binding on proposals (universe, caps, sizing, governor; §14 is the Scout-facing summary). The `.json` is the machine-readable twin. |
| `reference/RESEARCH_PRINCIPLES.md` | The full research framework (41 principles) that `AGENTS.md` §3 condenses; binding. |
| `reference/ALPHA_SOURCES.md` | Where to look for alpha: eight mechanism families with their generating questions, the nine conventions a hypothesis must satisfy, how to read external sources, and the inherited record of dead families. |
| `reference/IDEA_MAP_SEED.json` + `tools/seed_idea_map.py` | The 31-cell seed of the idea map (13 OPEN with a `next_test`, 18 CLOSED carrying the record of 140+ past tests) and the one-off script that creates them as `idea-map` issues in Linear (idempotent; `--dry-run` first). |
| `reference/REJECTION_PATTERNS.md` | The five ways 140+ past tests failed; every proposal must say why it is not one of them. |
| `reference/GLOSSARY.md` | Human names for the production sleeves and sizing vocabulary (`a4` FundingCarry, `a12` IlliquidityPremium, `a90x_ratio` TakerFlow-R, …). |
| `.agents/skills/research-scout/` | Scout's run skill: run dispatch, context-pack contents, proposal schema, the panel contract feature definitions write against. |
| `.agents/skills/data-and-backtest/` | Data model, the panel contract feature definitions are written against, point-in-time rules, the battery's target/windows/gates K1–K5, the adoption bar. |
| `.agents/skills/binance-futures-data/` | The S3 data bucket: candles, funding rates, open-interest metrics — layout, schemas, access, pitfalls. |
| `.claude/skills` | Symlink to `.agents/skills` so Claude Code discovers the skills. |

## What Scout touches, and what it never does

This is a config repo: it contains no executable research code, by design. Scout's whole surface is the Linear agent tools (records: `list_project_teams`, `create_issue`, `add_issue_comment`, `set_issue_status`, `attach_file_to_issue`, plus `read_issue` and `search_issues` for reads — searches paginate by cursor, up to 25 per page, most recently updated first), read-only S3 (the data bucket, for coverage and buildability checks), and local scratch.

Scout writes proposals whose feature definitions target the panel contract in the `research-scout` skill. The build, battery and verdict stages are not wired yet; when they are, Judge executes the submitted code and posts the `VERDICT` — Scout never runs a backtest and never sees battery output, which is what keeps the hypothesis-before-data discipline honest.

Scout assembles its own context pack from Linear at the start of every run (idea map, ledger tail, coverage map, open escalations, the count N — the `research-scout` skill lists the queries; the title prefixes `hypothesis:` / `idea-map:` / `escalation:` are the search keys), with the rejection patterns from `reference/` and the data catalogue from the S3 meta files plus the panel contract. There are no budget caps: the schedule is the budget (one idea per fresh run; cadence is a §9 human decision), and N — the count of hypothesis tickets — is always reported with any winner. Nothing else arrives with a run beyond the ticket itself, when there is one. Secrets are referenced by name only: `AWS_S3_ACCESS_KEY`, `AWS_S3_ACCESS_KEY_SECRET`. Linear needs no key in a run: it is connected as an integration on the agent (a personal API key held encrypted by the platform), and Scout acts in Linear as that key's user.

Two pieces therefore live outside this repo and must exist for the loop to run end to end: the **fresh-run trigger** — a schedule (ticket runs need no separate trigger: the Linear webhook routes an issue's events into the conversation that created it) — and **Judge's battery** that supplies the `panel` object per the contract in `data-and-backtest`, executes submitted `signal.py`, and posts verdicts. The battery does not exist yet; the specs here are its blueprint. Also note three panel inputs are unprovisioned in the data itself (market cap, premium index, full symbol tags — see `data-and-backtest` §1).

All state — hypotheses, critiques, revisions, the ledger, the idea map, escalations — lives in Linear per `AGENTS.md` §0.
