def ordered(processes):
    if not processes:
        raise ValueError("At least one process is required.")
    seen = set()
    result = []
    for index, p in enumerate(processes):
        pid = str(p.get("pid", "")).strip()
        arrival, burst = p.get("arrival"), p.get("burst")
        priority = p.get("priority", 1)
        if not pid:
            raise ValueError("Process IDs cannot be empty.")
        if pid in seen:
            raise ValueError(f"Duplicate process ID: {pid}")
        seen.add(pid)
        for key, value in (("arrival", arrival), ("burst", burst), ("priority", priority)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{key} for {pid} must be an integer.")
        if arrival < 0:
            raise ValueError(f"Arrival time for {pid} cannot be negative.")
        if burst <= 0:
            raise ValueError(f"Burst time for {pid} must be positive.")
        if priority < 1:
            raise ValueError(f"Priority for {pid} must be >= 1.")
        result.append({**p, "pid": pid, "arrival": arrival, "burst": burst,
                       "priority": priority, "_index": index})
    return result

def append_segment(segments, pid, start, end):
    if end <= start:
        return
    if segments and segments[-1]["pid"] == pid and segments[-1]["end"] == start:
        segments[-1]["end"] = end
    else:
        segments.append({"pid": pid, "start": start, "end": end})

def add_idle(segments, start, end):
    if end > start:
        append_segment(segments, "Idle", start, end)

def event(events, time, message):
    events.append({"Time": time, "Event": message, "message": f"t={time}: {message}"})
