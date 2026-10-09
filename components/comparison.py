import plotly.express as px

def make_comparison(df):
    long = df.melt(id_vars="Algorithm",
                   value_vars=["Avg Waiting", "Avg Turnaround", "Avg Response"],
                   var_name="Metric", value_name="Time")
    return px.bar(long, x="Algorithm", y="Time", color="Metric", barmode="group",
                  title="Scheduling algorithm performance comparison")
