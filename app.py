import streamlit as st
import pandas as pd
import plotly.express as px
from algorithms import schedule
from core.metrics import calculate_metrics, summarize_metrics
from components.gantt_chart import make_gantt
from components.comparison import make_comparison

st.set_page_config(page_title="OS Scheduling Visualizer", page_icon="⏱️", layout="wide")
st.title("⏱️ OS CPU Scheduling Visualizer")
st.caption("Explore CPU scheduling algorithms with interactive Gantt charts, metrics, and step-by-step execution.")

ALGORITHMS = ["FCFS", "SJF (Non-preemptive)", "SRTF (Preemptive SJF)", "Round Robin", "Priority (Non-preemptive)", "Priority (Preemptive)"]
DEFAULT = pd.DataFrame([
    {"Process": "P1", "Arrival Time": 0, "Burst Time": 7, "Priority": 3},
    {"Process": "P2", "Arrival Time": 2, "Burst Time": 4, "Priority": 1},
    {"Process": "P3", "Arrival Time": 4, "Burst Time": 1, "Priority": 2},
    {"Process": "P4", "Arrival Time": 5, "Burst Time": 4, "Priority": 4},
])

with st.sidebar:
    st.header("Simulation settings")
    algorithm = st.selectbox("Scheduling algorithm", ALGORITHMS)
    quantum = st.number_input("Round Robin time quantum", min_value=1, value=2, step=1)
    st.caption("Priority convention: 1 is the highest priority.")
    show_steps = st.checkbox("Show step-by-step simulation", value=True)
    st.markdown("---")
    st.markdown("**Metric definitions**")
    st.caption("TAT = CT − AT · WT = TAT − BT · RT = first CPU start − AT")

st.subheader("1. Define processes")
st.write("Edit the table directly. Process names must be unique; arrival times must be non-negative integers; burst times must be positive integers.")
edited = st.data_editor(
    DEFAULT,
    num_rows="dynamic",
    use_container_width=True,
    key="process_editor",
    column_config={
        "Process": st.column_config.TextColumn(required=True),
        "Arrival Time": st.column_config.NumberColumn(min_value=0, step=1, required=True),
        "Burst Time": st.column_config.NumberColumn(min_value=1, step=1, required=True),
        "Priority": st.column_config.NumberColumn(min_value=1, step=1, required=True),
    },
)
if st.button("Reset example processes"):
    st.session_state["process_editor"] = DEFAULT.copy()
    st.rerun()

def validate(frame):
    if frame.empty:
        return "Add at least one process."
    if frame[["Process", "Arrival Time", "Burst Time", "Priority"]].isnull().any().any():
        return "Fill in every cell."
    names = frame["Process"].astype(str).str.strip()
    if (names == "").any():
        return "Process names cannot be empty."
    if names.duplicated().any():
        return "Process names must be unique."
    for col in ["Arrival Time", "Burst Time", "Priority"]:
        values = pd.to_numeric(frame[col], errors="coerce")
        if values.isnull().any() or (values % 1 != 0).any():
            return f"{col} values must be integers."
    if (frame["Arrival Time"] < 0).any():
        return "Arrival times cannot be negative."
    if (frame["Burst Time"] <= 0).any():
        return "Burst times must be positive."
    if (frame["Priority"] < 1).any():
        return "Priorities must be integers greater than or equal to 1."
    return None

error = validate(edited)
if error:
    st.error(error)
    st.stop()

processes = [
    {"pid": str(row["Process"]).strip(), "arrival": int(row["Arrival Time"]),
     "burst": int(row["Burst Time"]), "priority": int(row["Priority"])}
    for _, row in edited.iterrows()
]
result = schedule(algorithm, processes, quantum=int(quantum))
metrics = calculate_metrics(processes, result["segments"])
summary = summarize_metrics(processes, result["segments"], metrics)

st.subheader("2. Execution timeline")
st.plotly_chart(make_gantt(result["segments"]), use_container_width=True)

if show_steps:
    st.subheader("3. Step-by-step simulation")
    events = result["events"]
    if events:
        max_step = len(events)
        step = st.slider("Simulation step", min_value=1, max_value=max_step, value=max_step)
        event = events[step - 1]
        st.info(f"Step {step}/{max_step}: {event['message']}")
        st.dataframe(pd.DataFrame(events[:step]), use_container_width=True, hide_index=True)
    else:
        st.info("No scheduling events to display.")

st.subheader("4. Per-process metrics")
metric_df = pd.DataFrame(metrics)
st.dataframe(metric_df, use_container_width=True, hide_index=True)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Average waiting time", f"{summary['avg_waiting']:.2f}")
c2.metric("Average turnaround time", f"{summary['avg_turnaround']:.2f}")
c3.metric("Average response time", f"{summary['avg_response']:.2f}")
c4.metric("CPU utilization", f"{summary['cpu_utilization']:.1f}%")
st.caption(f"Throughput: {summary['throughput']:.3f} processes/time unit · Makespan: {summary['makespan']}")

st.subheader("5. Compare algorithms")
comparison_rows = []
for alg in ALGORITHMS:
    r = schedule(alg, processes, quantum=int(quantum))
    m = calculate_metrics(processes, r["segments"])
    s = summarize_metrics(processes, r["segments"], m)
    comparison_rows.append({"Algorithm": alg, "Avg Waiting": s["avg_waiting"],
                            "Avg Turnaround": s["avg_turnaround"], "Avg Response": s["avg_response"],
                            "CPU Utilization (%)": s["cpu_utilization"], "Throughput": s["throughput"]})
comparison = pd.DataFrame(comparison_rows)
st.plotly_chart(make_comparison(comparison), use_container_width=True)
st.dataframe(comparison.round(3), use_container_width=True, hide_index=True)

with st.expander("Scheduling rules and assumptions"):
    st.markdown("""
    - **FCFS:** first arrived, first served; ties follow input order.
    - **SJF:** choose the shortest burst among processes that have arrived; non-preemptive.
    - **SRTF:** at each arrival/completion boundary, choose the shortest remaining time; ties keep the running process when possible, then input order.
    - **Round Robin:** FIFO ready queue with the configured time quantum.
    - **Priority:** lower numeric value means higher priority. Both preemptive and non-preemptive variants are available; ties use input order and, in preemptive mode, the current process is retained on equal priority.
    - Context-switch overhead is ignored. Idle time is represented explicitly in the Gantt chart.
    - CPU utilization is busy time divided by the elapsed interval from the earliest arrival to the final completion.
    """)
