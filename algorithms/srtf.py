from .common import ordered, append_segment, add_idle, event

def srtf(processes):
    ps = ordered(processes)
    rem = {p["pid"]: p["burst"] for p in ps}
    by_id = {p["pid"]: p for p in ps}
    done = set()
    t = min(p["arrival"] for p in ps)
    segments, events = [], []
    while len(done) < len(ps):
        ready = [p for p in ps if p["arrival"] <= t and p["pid"] not in done and rem[p["pid"]] > 0]
        if not ready:
            next_t = min(p["arrival"] for p in ps if p["pid"] not in done and p["arrival"] > t)
            add_idle(segments, t, next_t)
            event(events, t, f"CPU idle until {next_t}")
            t = next_t
            continue
        current_pid = segments[-1]["pid"] if segments and segments[-1]["pid"] != "Idle" else None
        p = min(ready, key=lambda x: (rem[x["pid"]], 0 if x["pid"] == current_pid else 1, x["_index"]))
        # Run until completion or the next arrival; reconsider at every arrival boundary.
        next_arrivals = [x["arrival"] for x in ps if x["arrival"] > t and x["pid"] not in done]
        boundary = min(next_arrivals) if next_arrivals else float("inf")
        run_for = min(rem[p["pid"]], boundary - t)
        start = t
        t += run_for
        rem[p["pid"]] -= run_for
        append_segment(segments, p["pid"], start, t)
        if rem[p["pid"]] == 0:
            done.add(p["pid"])
            event(events, t, f"{p['pid']} completes")
        else:
            event(events, t, f"Re-evaluate ready queue; {p['pid']} has {rem[p['pid']]} remaining")
    return {"segments": segments, "events": events}
