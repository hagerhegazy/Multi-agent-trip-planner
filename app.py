import asyncio
from pathlib import Path

import pandas as pd
import streamlit as st

from planner import run_trip

XLSX = Path(__file__).parent / "trip_budget.xlsx"
CHART = Path(__file__).parent / "charts" / "budget.png"

st.set_page_config(page_title="Trip Planner", page_icon="✈️", layout="wide")
st.markdown("""
<style>
html { font-size: 20px; }  /* scales everything: labels, buttons, sidebar, tables */

[data-testid="stWidgetLabel"] p,
.stCheckbox label p { font-size: 1.1rem !important; }

.stTextArea textarea { font-size: 1.15rem !important; line-height: 1.6; }
.stButton button p { font-size: 1.1rem !important; }

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] td,
[data-testid="stMarkdownContainer"] th { font-size: 1.1rem; line-height: 1.7; }
</style>
""", unsafe_allow_html=True)
st.title("✈️ Multi-Agent Trip Planner")

with st.sidebar:
    use_excel = st.checkbox("Save budget to Excel (via MCP)", value=True)

text = st.text_area(
    "Describe your trip",
    placeholder="e.g. 5 days in Rome in November, 2 people, mid-range, love food. Flying from Cairo.",
    height=120,
)

if st.button("Plan my trip", type="primary") and text.strip():
    for f in (XLSX, CHART):          # clean BEFORE the run so old files aren't shown
        if f.exists():
            f.unlink()
    status = st.status("Agents are working...", expanded=True)
    st.session_state.board = asyncio.run(
        run_trip(text, use_excel=use_excel, on_update=lambda n: status.write(f"✅ {n} finished"))
    )
    status.update(label="Done", state="complete", expanded=False)

board = st.session_state.get("board")
if board:
    st.markdown(board["final_plan"].replace("$", r"\$"))
    budget = board.get("budget", {})

    if CHART.exists():
        st.image(str(CHART), caption="Budget breakdown")
    elif budget.get("lines"):        # fallback if the MCP chart wasn't created
        df = pd.DataFrame(budget["lines"]).set_index("item")[["cost"]]
        st.bar_chart(df)

    if budget.get("excel_error"):
        st.warning(f"Excel save failed: {budget['excel_error']}")
    elif XLSX.exists():
        st.download_button("⬇️ Download budget (Excel)", XLSX.read_bytes(), "trip_budget.xlsx")

    with st.expander("Blackboard (what each agent wrote)"):
        st.json({k: v for k, v in board.items() if k != "final_plan"})