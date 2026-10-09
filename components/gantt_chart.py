import pandas as pd
import plotly.express as px

def make_gantt(segments):
    df = pd.DataFrame(segments)
    if df.empty:
        return px.scatter(title="No execution segments")
    df["Duration"] = df["end"] - df["start"]
    df["Label"] = df.apply(lambda r: f"{r['pid']}<br>{r['start']}–{r['end']}", axis=1)
    fig = px.bar(df, x="Duration", y="pid", color="pid", text="Label", orientation="h",
                 base="start", hover_data={"start": True, "end": True, "Duration": True, "pid": True},
                 labels={"pid": "Process", "Duration": "Time"})
    fig.update_traces(textposition="inside", insidetextanchor="middle")
    fig.update_layout(showlegend=False, xaxis_title="Time", yaxis_title="", bargap=0.25,
                      yaxis={"categoryorder": "array", "categoryarray": list(dict.fromkeys(df["pid"]))})
    return fig
