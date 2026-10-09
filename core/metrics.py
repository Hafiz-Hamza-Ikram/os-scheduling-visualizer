from algorithms.common import ordered

def calculate_metrics(processes, segments):
    ps = ordered(processes)
    first_start, completion = {}, {}
    busy = 0
    for seg in segments:
        pid, start, end = seg["pid"], seg["start"], seg["end"]
        if pid == "Idle":
            continue
        first_start.setdefault(pid, start)
        completion[pid] = end
        busy += end - start
    result = []
    for p in ps:
        pid = p["pid"]
        if pid not in completion:
            raise ValueError(f"No completion time found for {pid}.")
        ct = completion[pid]
        tat = ct - p["arrival"]
        wt = tat - p["burst"]
        rt = first_start[pid] - p["arrival"]
        result.append({"Process": pid, "Arrival Time": p["arrival"], "Burst Time": p["burst"],
                       "Priority": p["priority"], "Completion Time": ct,
                       "Turnaround Time": tat, "Waiting Time": wt, "Response Time": rt})
    return result

def summarize_metrics(processes, segments, metrics=None):
    if metrics is None:
        metrics = calculate_metrics(processes, segments)
    if not metrics:
        raise ValueError("At least one process is required.")
    # Measure utilization/throughput over the full displayed timeline, including leading idle time.
    start = min((s["start"] for s in segments), default=min(p["arrival"] for p in processes))
    end = max(s["end"] for s in segments) if segments else start
    elapsed = end - start
    busy = sum(s["end"] - s["start"] for s in segments if s["pid"] != "Idle")
    n = len(metrics)
    return {
        "avg_waiting": sum(m["Waiting Time"] for m in metrics) / n,
        "avg_turnaround": sum(m["Turnaround Time"] for m in metrics) / n,
        "avg_response": sum(m["Response Time"] for m in metrics) / n,
        "cpu_utilization": (busy / elapsed * 100) if elapsed > 0 else 0.0,
        "throughput": (n / elapsed) if elapsed > 0 else 0.0,
        "makespan": end,
    }
