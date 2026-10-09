from collections import deque
from .common import ordered, append_segment, add_idle, event

def round_robin(processes, quantum=2):
    ps = ordered(processes)
    if isinstance(quantum, bool) or not isinstance(quantum, int) or quantum <= 0:
        raise ValueError("Time quantum must be a positive integer.")
    by_arrival = sorted(ps, key=lambda p: (p["arrival"], p["_index"]))
    rem = {p["pid"]: p["burst"] for p in ps}
    q = deque()
    i, t = 0, 0
    segments, events = [], []
    while i < len(by_arrival) or q:
        if not q:
            if t < by_arrival[i]["arrival"]:
                add_idle(segments, t, by_arrival[i]["arrival"])
                event(events, t, f"CPU idle until {by_arrival[i]['arrival']}")
                t = by_arrival[i]["arrival"]
            while i < len(by_arrival) and by_arrival[i]["arrival"] <= t:
                q.append(by_arrival[i]["pid"])
                i += 1
        pid = q.popleft()
        start = t
        duration = min(quantum, rem[pid])
        t += duration
        rem[pid] -= duration
        append_segment(segments, pid, start, t)
        # Arrivals during the slice enter the queue before the preempted process is requeued.
        while i < len(by_arrival) and by_arrival[i]["arrival"] <= t:
            q.append(by_arrival[i]["pid"])
            i += 1
        if rem[pid] > 0:
            q.append(pid)
            event(events, t, f"{pid} quantum expires; {rem[pid]} remaining")
        else:
            event(events, t, f"{pid} completes")
    return {"segments": segments, "events": events}
