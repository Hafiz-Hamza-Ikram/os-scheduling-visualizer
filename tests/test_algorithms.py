import unittest
from algorithms import schedule
from core.metrics import calculate_metrics

PROCESSES = [
    {"pid": "P1", "arrival": 0, "burst": 7, "priority": 3},
    {"pid": "P2", "arrival": 2, "burst": 4, "priority": 1},
    {"pid": "P3", "arrival": 4, "burst": 1, "priority": 2},
    {"pid": "P4", "arrival": 5, "burst": 4, "priority": 4},
]

class SchedulingTests(unittest.TestCase):
    def test_fcfs(self):
        r = schedule("FCFS", PROCESSES)
        self.assertEqual([(s["pid"], s["start"], s["end"]) for s in r["segments"]],
                         [("P1", 0, 7), ("P2", 7, 11), ("P3", 11, 12), ("P4", 12, 16)])

    def test_sjf_nonpreemptive(self):
        r = schedule("SJF (Non-preemptive)", PROCESSES)
        self.assertEqual([(s["pid"], s["start"], s["end"]) for s in r["segments"]],
                         [("P1", 0, 7), ("P3", 7, 8), ("P2", 8, 12), ("P4", 12, 16)])

    def test_srtf_preempts(self):
        r = schedule("SRTF (Preemptive SJF)", PROCESSES)
        self.assertEqual([(s["pid"], s["start"], s["end"]) for s in r["segments"]],
                         [("P1", 0, 2), ("P2", 2, 4), ("P3", 4, 5), ("P2", 5, 7),
                          ("P4", 7, 11), ("P1", 11, 16)])

    def test_rr_total_cpu_time(self):
        r = schedule("Round Robin", PROCESSES, quantum=2)
        self.assertEqual(sum(s["end"] - s["start"] for s in r["segments"] if s["pid"] != "Idle"), 16)

    def test_priority_nonpreemptive(self):
        r = schedule("Priority (Non-preemptive)", PROCESSES)
        self.assertEqual(r["segments"][0]["pid"], "P1")
        self.assertEqual(r["segments"][1]["pid"], "P2")

    def test_metrics(self):
        r = schedule("FCFS", PROCESSES)
        m = {x["Process"]: x for x in calculate_metrics(PROCESSES, r["segments"])}
        self.assertEqual(m["P2"]["Completion Time"], 11)
        self.assertEqual(m["P2"]["Turnaround Time"], 9)
        self.assertEqual(m["P2"]["Waiting Time"], 5)
        self.assertEqual(m["P2"]["Response Time"], 5)

    def test_invalid_quantum(self):
        with self.assertRaises(ValueError):
            schedule("Round Robin", PROCESSES, quantum=0)

    def test_duplicate_process_rejected(self):
        bad = [PROCESSES[0], {**PROCESSES[1], "pid": "P1"}]
        with self.assertRaises(ValueError):
            schedule("FCFS", bad)

if __name__ == "__main__":
    unittest.main()
