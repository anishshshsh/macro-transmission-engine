import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from utils.data_loader import DataLoader
from engines.surprise_engine import MacroSurpriseEngine
from engines.reaction_engine import MarketReactionEngine
from engines.transmission_engine import TransmissionEngine


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Macro Transmission Engine",
    layout="wide"
)

project_root = Path(__file__).resolve().parents[1]

loader = DataLoader(project_root)

event_windows = loader.get_event_windows()
pre_event_window = loader.get_pre_event_window()

surprise_engine = MacroSurpriseEngine(
    loader.settings["surprise_vol_window"]
)

reaction_engine = MarketReactionEngine(
    event_windows,
    pre_event_window
)

transmission_engine = TransmissionEngine(event_windows)


# ---------------- LOAD MACRO DATA ----------------
macro_file = project_root / "data" / "macro" / "cpi.csv"
surprise_df = surprise_engine.build_surprise_series(macro_file)

st.title("📊 Macro Transmission Engine Dashboard")


# ---------------- EVENT SELECTOR ----------------
selected_date = st.selectbox(
    "Select CPI Event",
    surprise_df["date"]
)

latest_event = surprise_df[
    surprise_df["date"] == selected_date
].iloc[0]


# ---------------- KPI ROW ----------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "CPI Surprise (Z)",
        round(latest_event["surprise_z"], 2)
    )

with col2:
    percentile = (
        (surprise_df["surprise_z"] <= latest_event["surprise_z"]).mean()
    ) * 100

    st.metric(
        "Shock Percentile",
        f"{percentile:.0f}%"
    )

with col3:
    st.write("Event Date:", latest_event["date"].date())


# ---------------- SURPRISE HISTORY ----------------
st.subheader("Historical CPI Surprise")

st.line_chart(
    surprise_df.set_index("date")["surprise_z"]
)


# ---------------- COMPUTE REACTION ----------------
event_time = pd.Timestamp(
    f"{latest_event['date'].date()} 08:30",
    tz="US/Eastern"
)

assets = loader.load_all_assets()

start = (event_time - pd.Timedelta(days=20)).strftime("%Y-%m-%d")
end = (event_time + pd.Timedelta(days=20)).strftime("%Y-%m-%d")

reaction_results = {}

for group, asset in assets.items():

    iterable = asset if isinstance(asset, list) else [asset]

    for item in iterable:

        df = loader.fetch_market_data(
            item["ticker"],
            start,
            end
        )

        reactions = reaction_engine.compute_reactions(
            df,
            event_time,
            item["type"]
        )

        if reactions:
            reaction_results[item["name"]] = reactions


summary = transmission_engine.summarize_event(reaction_results)
event_matrix = summary["event_matrix"]


# ---------------- COVERAGE PANEL ----------------
valid_assets = len(event_matrix.index)
total_assets = sum(len(v) if isinstance(v, list) else 1 for v in assets.values())

st.info(f"Valid Reaction Coverage: {valid_assets} / {total_assets} assets")


# ---------------- REACTION BAR CHART ----------------
st.subheader("Cross Asset Reaction")

if event_matrix is None or event_matrix.empty:

    st.warning("No valid reactions for this event")

else:

    available_windows = list(event_matrix.columns)

    selected_window = st.selectbox(
        "Select Reaction Horizon",
        available_windows,
        index=len(available_windows) - 1
    )

    fig, ax = plt.subplots(figsize=(6, 3))

    ax.bar(
        event_matrix.index,
        event_matrix[selected_window]
    )

    ax.set_title(f"Reaction at {selected_window}")

    plt.xticks(rotation=30)

    st.pyplot(fig)


# ---------------- MATRIX TABLE ----------------
st.subheader("Transmission Matrix")

st.dataframe(event_matrix)


# ---------------- BUILD HISTORICAL REACTION DATASET ----------------
historical_results = []

for _, event in surprise_df.iterrows():

    event_time_loop = pd.Timestamp(
        f"{event['date'].date()} 08:30",
        tz="US/Eastern"
    )

    start_loop = (event_time_loop - pd.Timedelta(days=10)).strftime("%Y-%m-%d")
    end_loop = (event_time_loop + pd.Timedelta(days=10)).strftime("%Y-%m-%d")

    for group, asset in assets.items():

        iterable = asset if isinstance(asset, list) else [asset]

        for item in iterable:

            df = loader.fetch_market_data(
                item["ticker"],
                start_loop,
                end_loop
            )

            reactions = reaction_engine.compute_reactions(
                df,
                event_time_loop,
                item["type"]
            )

            if "1440m" in reactions:

                historical_results.append({
                    "asset": item["name"],
                    "reaction": reactions["1440m"],
                    "surprise_z": event["surprise_z"]
                })

historical_df = pd.DataFrame(historical_results).dropna()


# ---------------- DISTRIBUTION ----------------
st.subheader("Reaction Distribution")

if not historical_df.empty:

    selected_asset = st.selectbox(
        "Select Asset for Distribution",
        historical_df["asset"].unique()
    )

    dist_data = historical_df[
        historical_df["asset"] == selected_asset
    ]["reaction"]

    fig2, ax2 = plt.subplots(figsize=(6, 3))

    ax2.hist(dist_data, bins=15)

    st.pyplot(fig2)


# ---------------- SCATTER ----------------
st.subheader("Shock Sensitivity Scatter")

if not historical_df.empty:

    scatter = historical_df[
        historical_df["asset"] == selected_asset
    ]

    fig3, ax3 = plt.subplots(figsize=(6, 3))

    ax3.scatter(
        scatter["surprise_z"],
        scatter["reaction"],
        alpha=0.6
    )

    st.pyplot(fig3)