from .fcfs import fcfs
from .sjf import sjf
from .srtf import srtf
from .round_robin import round_robin
from .priority import priority_schedule

def schedule(name, processes, quantum=2):
    if name == "FCFS":
        return fcfs(processes)
    if name == "SJF (Non-preemptive)":
        return sjf(processes)
    if name == "SRTF (Preemptive SJF)":
        return srtf(processes)
    if name == "Round Robin":
        return round_robin(processes, quantum)
    if name == "Priority (Non-preemptive)":
        return priority_schedule(processes, preemptive=False)
    if name == "Priority (Preemptive)":
        return priority_schedule(processes, preemptive=True)
    raise ValueError(f"Unknown algorithm: {name}")
