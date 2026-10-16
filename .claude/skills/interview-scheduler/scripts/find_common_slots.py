#!/usr/bin/env python3
"""Find interview slots where every required panelist is free.

Usage: find_common_slots.py interview_brief.json [--step 30] [--json]

Reads brief["availability"]: {panelist_email: [{"start": "YYYY-MM-DDTHH:MM", "end": ..., "tz": "Area/City"}]}
Optional panel entry flag "optional": true excludes that panelist from the intersection
(near-miss output still reports them). Prints slots in UTC, coordinator TZ and candidate TZ.
"""
import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


def to_utc(stamp, tz):
    dt = datetime.fromisoformat(stamp)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(tz))
    return dt.astimezone(timezone.utc)


def merge(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], e))
        else:
            out.append((s, e))
    return out


def intersect(a, b):
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        s, e = max(a[i][0], b[j][0]), min(a[i][1], b[j][1])
        if s < e:
            out.append((s, e))
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return out


def slots_in(free, duration, step):
    out = []
    for s, e in free:
        # align start to the step grid so proposals look like 14:00 / 14:30, not 14:07
        minute = (s.minute // step) * step
        cur = s.replace(minute=minute, second=0, microsecond=0)
        if cur < s:
            cur += timedelta(minutes=step)
        while cur + duration <= e:
            out.append(cur)
            cur += timedelta(minutes=step)
    return out


def fmt(dt, tz):
    return dt.astimezone(ZoneInfo(tz)).strftime("%a %d %b %Y %H:%M") + f" {tz}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brief")
    ap.add_argument("--step", type=int, default=30, help="slot granularity in minutes")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    brief = json.load(open(args.brief))
    iv = brief["interview"]
    duration = timedelta(minutes=int(iv.get("duration_min", 60)))
    coord_tz = iv.get("coordinator_tz") or "UTC"
    cand_tz = brief.get("candidate", {}).get("timezone") or coord_tz
    avail = brief.get("availability", {})
    panel = brief.get("panel", [])
    required = [p["email"] for p in panel if not p.get("optional")]

    missing = [e for e in required if not avail.get(e)]
    if missing:
        print("Missing availability for: " + ", ".join(missing), file=sys.stderr)
        sys.exit(2)

    per_person = {
        e: merge([(to_utc(w["start"], w.get("tz", coord_tz)), to_utc(w["end"], w.get("tz", coord_tz))) for w in avail[e]])
        for e in avail
    }

    common = per_person[required[0]]
    for e in required[1:]:
        common = intersect(common, per_person[e])
    slots = slots_in(common, duration, args.step)

    def describe(start):
        local = start.astimezone(ZoneInfo(cand_tz))
        end_local = (start + duration).astimezone(ZoneInfo(cand_tz))
        ok = 8 <= local.hour and (end_local.hour, end_local.minute) <= (19, 0) and local.date() == end_local.date()
        return {
            "utc": start.strftime("%Y-%m-%dT%H:%MZ"),
            "coordinator": fmt(start, coord_tz),
            "candidate": fmt(start, cand_tz),
            "candidate_working_hours": ok,
        }

    result = {"duration_min": int(duration.total_seconds() // 60), "slots": [describe(s) for s in slots]}

    if not slots:
        # near misses: drop each person in turn and see what opens up
        near = {}
        for skip in required:
            others = [e for e in required if e != skip]
            if not others:
                continue
            c = per_person[others[0]]
            for e in others[1:]:
                c = intersect(c, per_person[e])
            s = slots_in(c, duration, args.step)
            if s:
                near[skip] = [describe(x) for x in s[:3]]
        result["near_misses_without"] = near

    if args.json:
        print(json.dumps(result, indent=2))
        return
    if slots:
        print(f"{len(slots)} common {result['duration_min']}-min slot(s):")
        for d in result["slots"]:
            flag = "" if d["candidate_working_hours"] else "  [outside candidate 08-19]"
            print(f"  {d['coordinator']}  |  candidate: {d['candidate']}{flag}")
    else:
        print("No slot where all required panelists are free.")
        for who, opts in result.get("near_misses_without", {}).items():
            print(f"  Possible if {who} is excluded: " + "; ".join(o["coordinator"] for o in opts))


if __name__ == "__main__":
    main()
