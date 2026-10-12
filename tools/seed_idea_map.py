#!/usr/bin/env python3
"""Seed the idea map into Linear (team NoSyntax, label `idea-map`) from reference/IDEA_MAP_SEED.json — run ONCE, idempotent.

One Linear issue per cell: title "<id> — <title>", description = the cell JSON (plus a one-line summary), label `idea-map`,
state = an unstarted workflow state for OPEN cells and a completed state for CLOSED cells. Existing issues (same title, same
team) are left alone, so re-running is safe. This is tooling, not research code; Scout never runs it.

    LINEAR_API_KEY=... python3 tools/seed_idea_map.py --dry-run          # print what would be created, no API writes
    LINEAR_API_KEY=... python3 tools/seed_idea_map.py                    # create
    options: --team NoSyntax --label idea-map --open-state Backlog --closed-state Done --seed reference/IDEA_MAP_SEED.json
Needs only the standard library. The key is read from the environment and never printed.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request

API = "https://api.linear.app/graphql"


def gql(query, variables=None):
    key = os.environ.get("LINEAR_API_KEY")
    if not key:
        sys.exit("LINEAR_API_KEY is not set")
    req = urllib.request.Request(API, data=json.dumps({"query": query, "variables": variables or {}}).encode(), headers={"Content-Type": "application/json", "Authorization": key})
    with urllib.request.urlopen(req, timeout=60) as r:
        out = json.load(r)
    if out.get("errors"):
        sys.exit(f"Linear error: {out['errors']}")
    return out["data"]


def team_id(name):
    for t in gql("query { teams { nodes { id name key } } }")["teams"]["nodes"]:
        if t["name"] == name or t["key"] == name:
            return t["id"]
    sys.exit(f"team {name!r} not found")


def label_id(tid, name):
    for l in gql("query($t:String!){ issueLabels(filter:{team:{id:{eq:$t}}}) { nodes { id name } } }", {"t": tid})["issueLabels"]["nodes"]:
        if l["name"] == name:
            return l["id"]
    return gql("mutation($t:String!,$n:String!){ issueLabelCreate(input:{teamId:$t,name:$n}) { issueLabel { id } } }", {"t": tid, "n": name})["issueLabelCreate"]["issueLabel"]["id"]


def state_ids(tid, open_name, closed_name):
    st = gql("query($t:String!){ workflowStates(filter:{team:{id:{eq:$t}}}) { nodes { id name type position } } }", {"t": tid})["workflowStates"]["nodes"]
    def pick(name, typ):
        for s in st:
            if s["name"].lower() == (name or "").lower():
                return s["id"]
        cands = sorted([s for s in st if s["type"] == typ], key=lambda s: s["position"])
        if not cands:
            sys.exit(f"no workflow state of type {typ}")
        return cands[0]["id"]
    return pick(open_name, "unstarted"), pick(closed_name, "completed")


def existing_titles(tid, label):
    titles = set(); after = None
    while True:
        d = gql("query($t:String!,$l:String!,$a:String){ issues(first:100, after:$a, filter:{team:{id:{eq:$t}}, labels:{name:{eq:$l}}}) { nodes { title } pageInfo { hasNextPage endCursor } } }", {"t": tid, "l": label, "a": after})["issues"]
        titles.update(n["title"] for n in d["nodes"])
        if not d["pageInfo"]["hasNextPage"]:
            return titles
        after = d["pageInfo"]["endCursor"]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--seed", default=os.path.join(os.path.dirname(__file__), "..", "reference", "IDEA_MAP_SEED.json"))
    ap.add_argument("--team", default="NoSyntax"); ap.add_argument("--label", default="idea-map"); ap.add_argument("--open-state"); ap.add_argument("--closed-state"); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    cells = json.load(open(a.seed, encoding="utf-8"))["cells"]
    plan = []
    for c in cells:
        title = f"{c['id']} — {c['title']}"
        body = (f"**{c['mechanism_family']} × {c['data_family']}** · status {c['status']} · priority {c.get('priority', 0)} · scores {json.dumps(c['scores'])}\n\n"
                f"next_test: {c.get('next_test') or '—'}\n\nnotes: {c.get('notes') or '—'}\n\nledger_refs (external ids from the inherited record): {', '.join(c.get('ledger_refs') or []) or '—'}\n\n```json\n{json.dumps(c, indent=1, ensure_ascii=False)}\n```")
        plan.append((title, body, c["status"]))
    if a.dry_run:
        for t, _, s in plan:
            print(f"[{s:6s}] {t}")
        print(f"{len(plan)} cells (dry run; nothing written)"); return
    tid = team_id(a.team); lid = label_id(tid, a.label); open_id, closed_id = state_ids(tid, a.open_state, a.closed_state); have = existing_titles(tid, a.label)
    made = skipped = 0
    for title, body, status in plan:
        if title in have:
            skipped += 1; continue
        gql("mutation($i:IssueCreateInput!){ issueCreate(input:$i) { success issue { identifier } } }",
            {"i": {"teamId": tid, "title": title, "description": body, "labelIds": [lid], "stateId": closed_id if status == "CLOSED" else open_id}})
        made += 1; print("created", title)
    print(f"done: {made} created, {skipped} already existed")


if __name__ == "__main__":
    main()
