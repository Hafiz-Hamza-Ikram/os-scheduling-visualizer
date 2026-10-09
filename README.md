# OS CPU Scheduling Visualizer

Interactive Streamlit app for FCFS, non-preemptive SJF, preemptive SJF/SRTF, Round Robin, and preemptive/non-preemptive Priority Scheduling.

## Requirements
- Python 3.10+
- Packages in `requirements.txt`

## Run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Tests
```bash
python -m unittest discover -s tests -v
```

## Notes
- Priority `1` is highest.
- Arrival/burst/priority are integers; burst must be positive.
- Context-switch overhead is ignored.
- Idle CPU time is shown in the timeline.
- Round Robin quantum must be positive.
