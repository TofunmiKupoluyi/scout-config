---
name: trade-config-spec
description: "Use whenever you write, revise or validate a trade config for Judge: the data fields you may use (all point-in-time and lagged for you), the signal operations, the positions and schedule rules, the JSON schema, parameter ranges for the sweep, common mistakes that make a config fail validation, and worked examples. No backtest or risk knowledge needed — the engine applies those."
---

# Trade config spec (schema 1.0)

A trade config is a small JSON document that says **what is ranked, who is bought and sold, how much, and how often**. Judge's engine reads nothing else. You never specify costs, limits, leverage, hedging, test windows or pass criteria — the engine adds them identically to every config, so two configs are compared on the trade idea alone.

Reference files (same directory tree): `reference/TRADE_CONFIG_SCHEMA.json` (the schema), `tools/validate_config.py` (run it on every config before posting), `examples/*.json` (four complete configs).

## 1. How the engine reads your config (what you can rely on)
- **Daily, cross-sectional.** Every data field is a table with one row per UTC day `t` and one column per symbol. The row at `t` contains only information from BEFORE `t` 00:00 UTC. You cannot look ahead; you do not need to lag anything.
- **Signal → ranking.** Your `signal.steps` turn fields into one output series. **Higher output = more attractive to be LONG.** If your idea is "sell the names with high X", end with a `neg` step or rank on `-X` — never rely on the engine guessing the sign.
- **Universe.** The engine ranks only eligible names: perpetuals with a 21-day median daily volume above `universe.min_mdv_usd` (default $3M, with a stay-in band so names do not flicker), listed for at least `min_age_days` (default 30), BTCUSDT excluded (it is the hedge instrument, never a signal name). You may raise the floor or restrict `include_only`; you cannot lower it below what the data supports.
- **Positions.** On each rebalance day the engine takes the ranked eligible names and applies `positions.mode`: `top_bottom_n` (N longs, N shorts), `quantile` (top/bottom fraction), `threshold` (long above / short below a value of the output), or `proportional` (every name, weight ∝ demeaned output). `weighting` = `equal`, `signal` (∝ distance from the cross-sectional median), or `rank`. Size is either `side_gross_pct` (target gross per side, % of notional; 50 = one times notional in total) or `per_name_bps` (fixed bps of notional per name). `long` / `short` can switch a leg off.
- **Schedule.** `rebalance` ∈ `1d 2d 3d 1w 2w` (`1w`/`2w` anchor on Mondays by default); `holding_days` = how long an entry is held (default = the rebalance interval; overlapping entries are averaged, which is how a 1-day rebalance with a 7-day hold becomes a seven-tranche ladder); `delay_days` adds execution delay beyond the built-in lag (rarely needed).
- **Everything else is the engine's**: trading costs, funding paid or received, per-name and total exposure limits, the BTC hedge that keeps the book market-neutral, the test windows, the sweep, the stress tests and the pass bar. A config that needs any of these to be different is not a valid proposal — mention it in `notes` instead.

## 2. Data fields (`{"op": "field", "name": …}`)
All are per-day, per-symbol, known at `t` 00:00 UTC. "day t−1" = the UTC day that just ended.

| field | meaning | typical use |
|---|---|---|
| `close` | last price at t 00:00 | levels, momentum via `pct_change` |
| `ret` | simple return close_t / close_{t−1} − 1 | returns, reversal, volatility |
| `log_ret` | ln(close_t / close_{t−1}) | compounding sums |
| `resid_ret` | `ret` minus the name's 60-day beta × BTC return (BTC-residual) | market-neutral momentum / reversal |
| `btc_ret` | BTC's `ret`, broadcast to every column | conditioning on the market |
| `high`, `low` | day t−1's high / low | ranges |
| `range_pct` | (high − low) / close_{t−1} | intraday range, a vol proxy |
| `hl_spread_1m` | day t−1's mean over its 1-minute bars of (high − low) / close | spread / liquidity proxy; market-maker withdrawal |
| `hl_spread_1m_median` | median of the same per-minute values | robust version; exactly 0 when most minutes traded at one price, so near-zero means thin, not tight |
| `volume_usd` | day t−1's quote volume in USD | activity, Amihud, attention |
| `taker_buy_usd`, `taker_sell_usd` | day t−1's aggressive buy / sell volume in USD | flow |
| `taker_imbalance` | (buy − sell) / volume, in [−1, 1] | net aggression |
| `n_trades` | day t−1's trade count | retail activity, average trade size via `div` |
| `funding` | funding paid by a LONG over day t−1 (sum of prints; positive = longs paid) | carry, crowding |
| `funding_3d` | 3-day sum of `funding` | smoother carry |
| `mdv21` | 21-day median daily USD volume | liquidity tier, size proxy |
| `adv7` | 7-day mean daily USD volume | recent activity |
| `amihud21` | 21-day mean of abs(ret) / volume_usd | price impact per dollar (illiquidity) |
| `vol30` | 30-day standard deviation of `ret` | volatility |
| `oi_usd` | open interest in USD at the end of day t−1 | leverage, crowding (÷ `mdv21`) |
| `oi_change_1d` | oi_usd / previous − 1 | leverage build-up / unwind |
| `ls_ratio_acct` | long/short ratio by number of accounts (retail positioning) | crowd positioning |
| `ls_ratio_top_acct` | same, top traders by account | smart-money positioning |
| `ls_ratio_top_pos` | top traders by position size | smart-money positioning |
| `taker_ls_vol` | taker buy/sell volume ratio from the exchange's metrics feed | flow confirmation |
| `age_days` | days since the first candle | listing effects, filters |
| `mcap` | market cap — **not provisioned (all NaN)**; a config that depends on it will have no names | do not use |

Hourly and minute data exist in the bucket but are **not exposed** as fields in schema 1.0; an intraday idea must be expressed through the daily aggregates above (e.g. `taker_imbalance`, `range_pct`, `hl_spread_1m`, `n_trades`) or escalated as a data request. Unlike `range_pct` (one daily range, mostly volatility), `hl_spread_1m` averages 1,440 one-minute ranges, so it reflects bid-ask bounce and depth; the two are different measurements, not substitutes.

## 3. Signal operations (`signal.steps` — a list evaluated top to bottom; each step names its `out`)
Every step has `op` and `out` (snake_case). Inputs refer to the `out` of earlier steps. Numbers may be literals or `"$param"` references.

| op | arguments | result |
|---|---|---|
| `field` | `name` | the data field |
| `const` | `value` | a constant table |
| `rolling_mean` `rolling_sum` `rolling_std` `rolling_max` `rolling_min` `rolling_median` | `in`, `window` (days), optional `min_periods` (default 70% of window) | rolling statistic over the last `window` days |
| `ewm_mean` | `in`, `window` (= span in days) | exponentially weighted mean |
| `lag` | `in`, `window` | the value `window` days earlier |
| `diff` | `in`, `window` | value − value `window` days earlier |
| `pct_change` | `in`, `window` | value / value `window` days earlier − 1 (e.g. momentum from `close`) |
| `zscore_time` | `in`, `window` | (x − rolling mean) / rolling std per name over `window` days |
| `log` `abs` `neg` `sign` | `in` | elementwise (log of non-positive = NaN) |
| `clip` | `in`, `lo` and/or `hi` | winsorise |
| `add` `sub` `mul` `div` `pow` | `a`, `b` | elementwise (`div` by 0 = NaN) |
| `cross_rank` | `in` | percentile rank across names each day, in (0, 1] |
| `cross_zscore` | `in` | (x − daily cross-sectional mean) / std |
| `cross_demean` | `in` | x − daily cross-sectional mean |
| `gt` `lt` | `in`, `threshold` | 1.0 where true, 0.0 where false (NaN stays NaN) |
| `and` `or` | `a`, `b` | boolean combination of 0/1 tables |
| `where` | `cond`, `then`, `else` | pick `then` where cond > 0 else `else` |

`signal.output` names the step whose `out` is the ranking. Rankings are compared across names on the same day, so scale does not matter — but NaN does: a name whose output is NaN on a rebalance day is simply not traded. Use `min_periods` deliberately when a long window would otherwise leave young names out.

Patterns: momentum = `field close → pct_change window` ; reversal = `field resid_ret → rolling_sum window → neg` ; crowding = `field oi_usd`, `field mdv21`, `div` ; carry = `field funding_3d → neg` (longs receive when funding is negative) ; conditioning = build a 0/1 `gt`/`lt` table and `mul` it into the ranking, or use `where` to switch between two rankings ; interaction = `cross_rank` both pieces, then `mul` or `add`.

## 4. Parameters, ranges and alternatives (what Judge sweeps)
```json
"params": {"lookback_days": {"value": 21, "range": [10, 42], "unit": "days", "integer": true},
           "n": {"value": 10, "range": [5, 20], "unit": "count", "integer": true},
           "thresh": {"value": 0.02, "unit": "ratio"}}
```
- Reference a parameter anywhere a number is allowed as `"$lookback_days"`.
- `range` = `[min, max]` Judge may try (five points inside it, including your value). The value must lie in the range. Give a range to every number you chose by judgement; pin (omit `range`) the ones the mechanism fixes. Keep ranges tied to the mechanism's time scale (a 3-day flow effect gets `[2, 7]`, not `[1, 90]`).
- `alternatives` lists other constructions Judge may also try: `positions.mode`, `positions.weighting`, `schedule.rebalance`, and `signal.output` (another step of the same idea, e.g. a z-scored vs a raw version). Only list alternatives that are equally faithful to the mechanism — Judge treats every listed option as part of your framework.
- Judge selects the best combination on its calibration data only and reports the untouched remainder; the whole grid is reported, so a knife-edge optimum is visible. Fewer, better-motivated ranges beat wide ones.

## 5. Writing a config that validates first time
1. Start from the closest file in `examples/` and change it; do not write from a blank page.
2. Required top-level keys: `schema_version` ("1.0"), `hypothesis` (one line, 10–300 chars), `framework` (20–1200 chars plain words), `signal`, `positions`, `schedule`. Optional: `experiment`, `round`, `universe`, `params`, `alternatives`, `notes`. Nothing else is allowed (the schema has `additionalProperties: false` everywhere).
3. Every `in`/`a`/`b`/`cond`/`then`/`else` must name an `out` produced EARLIER in the list. Every `$param` must exist in `params`. Every `field` name must be in the table above.
4. `positions.mode` needs its key: `n` for `top_bottom_n`, `quantile` (0 < q ≤ 0.5) for `quantile`, `long_above`/`short_below` for `threshold`.
5. Choose ONE of `side_gross_pct` or `per_name_bps`. Defaults: equal weight, 50% per side, both legs on.
6. `schedule.rebalance` is one of `1d 2d 3d 1w 2w`; `holding_days` 1–60 if given.
7. Run `python3 tools/validate_config.py config.json`. It prints `valid: …` and the parameter table, or `error: …` lines with the step index. Warnings (e.g. "the signal is a raw field") are worth reading: they usually mean a missing transformation.
8. Put the validated JSON under the plain-words framework in the ticket (`reference/TICKET_FORMAT.md`). The plain words and the JSON must say the same thing.

Common errors: forgetting `neg` for a "short the high values" idea; using `mcap`; a `range` that does not contain `value`; a `window` of 0; referring to a step defined later; `quantile` above 0.5; `per_name_bps` together with `side_gross_pct`; keys the schema does not know (`costs`, `leverage`, `stop_loss`, `max_dd` — these are not yours to set).

## 6. Worked example (the brief's own)
Hypothesis: *Holding illiquid assets yields a premium over time.* Framework: rank by Amihud illiquidity over 21 days, buy the 10 least liquid, sell the 10 most liquid, 50 bps of notional per name, weekly on Mondays, one-week hold. See `examples/example_illiquidity_top10.json` for the JSON (`ret → abs`, `volume_usd`, `div`, `rolling_mean $lookback_days`, `log` → `illiq`; `top_bottom_n` with `$n`; `per_name_bps: 50`; `1w` Monday, 7-day hold; ranges 10–42 days and 5–20 names; alternatives rank-weighting and a two-week rebalance). The other three examples (`ref_funding_carry`, `ref_illiquidity`, `ref_taker_flow`) show a conditioned carry sort, a quantile construction, and a flow ratio with `clip`.
