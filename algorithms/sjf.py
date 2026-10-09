from .common import ordered, append_segment, add_idle, event

def sjf(processes):
    ps = ordered(processes)
    remaining = {p["pid"]: p for p in ps}
    t = 0
    segments, events = [], []
    while remaining:
        available = [p for p in remaining.values() if p["arrival"] <= t]
        if not available:
            next_arrival = min(p["arrival"] for p in remaining.values())
            add_idle(segments, t, next_arrival)
            event(events, t, f"CPU idle until {next_arrival}")
            t = next_arrival
            continue
        p = min(available, key=lambda x: (x["burst"], x["arrival"], x["_index"]))
        start = t
        t += p["burst"]
        append_segment(segments, p["pid"], start, t)
        event(events, start, f"Selected {p['pid']} (burst={p['burst']}); completes at t={t}")
        del remaining[p["pid"]]
    return {"segments": segments, "events": events}
