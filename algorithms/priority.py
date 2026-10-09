from .common import ordered, append_segment, add_idle, event

def priority_schedule(processes, preemptive=False):
    ps = ordered(processes)
    remaining = {p["pid"]: p["burst"] for p in ps}
    done = set()
    t = 0
    segments, events = [], []
    while len(done) < len(ps):
        ready = [p for p in ps if p["arrival"] <= t and p["pid"] not in done and remaining[p["pid"]] > 0]
        if not ready:
            future = [p["arrival"] for p in ps if p["pid"] not in done and p["arrival"] > t]
            if not future:
                break
            next_t = min(future)
            add_idle(segments, t, next_t)
            event(events, t, f"CPU idle until {next_t}")
            t = next_t
            continue
        current_pid = segments[-1]["pid"] if segments and segments[-1]["pid"] != "Idle" else None
        p = min(ready, key=lambda x: (x["priority"], 0 if x["pid"] == current_pid else 1, x["_index"]))
        start = t
        if preemptive:
            future = [x["arrival"] for x in ps if x["arrival"] > t and x["pid"] not in done]
            next_arrival = min(future) if future else float("inf")
            duration = min(remaining[p["pid"]], next_arrival - t)
        else:
            duration = remaining[p["pid"]]
        t += duration
        remaining[p["pid"]] -= duration
        append_segment(segments, p["pid"], start, t)
        if remaining[p["pid"]] == 0:
            done.add(p["pid"])
            event(events, t, f"{p['pid']} completes (priority={p['priority']})")
        else:
            event(events, t, f"Re-evaluate priority queue; {p['pid']} has {remaining[p['pid']]} remaining")
    return {"segments": segments, "events": events}
