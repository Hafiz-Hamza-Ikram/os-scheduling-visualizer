from .common import ordered, append_segment, add_idle, event

def fcfs(processes):
    ps = ordered(processes)
    queue = sorted(ps, key=lambda p: (p["arrival"], p["_index"]))
    t = 0
    segments, events = [], []
    for p in queue:
        if t < p["arrival"]:
            add_idle(segments, t, p["arrival"])
            event(events, t, f"CPU idle until {p['arrival']}")
            t = p["arrival"]
        start = t
        t += p["burst"]
        append_segment(segments, p["pid"], start, t)
        event(events, start, f"{p['pid']} starts; runs to t={t}")
    return {"segments": segments, "events": events}
