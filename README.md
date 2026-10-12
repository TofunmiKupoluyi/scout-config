# scout-config

Configuration for **Scout**, agent A of a two-agent alpha-research desk on Binance USDT-M perpetual futures (market-neutral, cross-sectional). Scout generates ideas; **Judge** (its own repo, `judge-config`) tests them. Every run is a fresh-context session; Linear (team **NoSyntax**) is the only memory.

## What Scout produces, every time
1. **An alpha hypothesis** — one line, plain words ("Holding illiquid assets yields a premium over time").
2. **A trade framework** that would capture it — plain words a trader can read (rank by X over 21 days, buy the top 10, sell the bottom 10, 50 bps a name, weekly).
3. **A trade config** — the framework as JSON in the schema Judge's engine reads (`reference/TRADE_CONFIG_SCHEMA.json`), validated with `tools/validate_config.py` before posting.

Scout does **not** know the backtest or risk side (costs, limits, hedge, windows, pass bar) — by design. The config describes only the trade; Judge's engine applies everything else identically to every config.

## The loop (one Linear issue per experiment; four statuses)
```
Scout: create issue  ──► Idea Generated ──► Judge runs it ──► PASS ──► Human Review
                              ▲                  │
                              │                 FAIL (round < 5)
          [SCOUT FRAMEWORK n/5]│                  ▼
          new framework, same  └──────────── Critiqued
          hypothesis                              │ no materially different framework / hard blocker
                                                  ▼
                                   FAIL at round 5 ─────────────► Discarded
```
Maximum five frameworks per hypothesis. A new framework is a different *construction* (observable, conditioning, horizon class, universe slice, leg), never a parameter change — Judge already swept the ranges Scout declared. Exact ticket layout and transitions: `reference/TICKET_FORMAT.md`.

## Layout
| Path | What it is |
|---|---|
| `AGENTS.md` | Scout's master prompt. §0 Linear protocol and the four statuses, §4 the two run kinds, §5 the quality bar, §8 the human decisions. |
| `.agents/skills/research-scout/` | Run procedure: dispatch, Linear tools, context pack, how to write the three deliverables, how to design round 2–5 from a FAIL. |
| `.agents/skills/trade-config-spec/` | The config language: data fields (all point-in-time), signal operations, positions and schedule rules, parameter ranges, validation, worked example. |
| `.agents/skills/binance-futures-data/` | The S3 bucket layout (Scout uses it for metadata only — which symbols, which fields, from when). |
| `reference/TRADE_CONFIG_SCHEMA.json` | JSON schema 1.0 of a trade config (identical copy in judge-config). |
| `reference/TICKET_FORMAT.md` | What goes in the issue description, the `[SCOUT FRAMEWORK n/5]` and `[JUDGE RESULT n/5]` comments, and the status transitions (identical copy in judge-config). |
| `reference/ALPHA_SOURCES.md` | Where to look: eight mechanism families with generating questions, the nine conventions an experiment must satisfy. |
| `reference/WHAT_FAILED_BEFORE.md` | The inherited record of 140+ dead tests, as plain-words patterns (no test numbers). |
| `reference/RESEARCH_PRINCIPLES.md` | The desk's research stance (mechanism first, simplicity, suspicion of data). |
| `reference/GLOSSARY.md` | Human names of the known sleeves (FundingCarry, IlliquidityPremium, TakerFlow) so a "costume" of one can be recognised. |
| `reference/IDEA_MAP_SEED.json` + `tools/seed_idea_map.py` | 31-cell idea-map seed and the one-off script that creates the `idea-map:` issues in Linear (idempotent; `--dry-run` first; needs `LINEAR_API_KEY` in the environment of whoever runs it — never Scout). |
| `tools/validate_config.py` | Stdlib validator (schema + semantic rules); `python3 tools/validate_config.py cfg.json`. Same file as in judge-config. |
| `examples/` | Four complete configs: the brief's worked example (Amihud top/bottom 10) and three reference constructions (funding carry, illiquidity quantile, taker-flow ratio). |
| `.claude/skills` | Symlink to `.agents/skills` so Claude Code discovers the skills. |

## What must exist outside this repo
- The four Linear workflow statuses in team NoSyntax, named exactly **Idea Generated**, **Critiqued**, **Discarded**, **Human Review** (`list_project_teams` must return them).
- The fresh-run trigger (a schedule) — ticket runs arrive through the Linear webhook into the conversation that created the issue.
- Judge, with the engine (`judge-config/tools/judge_run.py`), the data bucket credentials (`AWS_S3_ACCESS_KEY`, `AWS_S3_ACCESS_KEY_SECRET`, referenced by name only) and Python with pandas/pyarrow/s3fs. Scout needs only Python 3 for the validator.

Scout never computes on market data, never runs a backtest, never sets Human Review, and never touches production.
