import sys
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from utils.data_loader import DataLoader
from engines.surprise_engine import MacroSurpriseEngine
from engines.reaction_engine import MarketReactionEngine
from engines.transmission_engine import TransmissionEngine


def generate_macro_report(project_root):

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

    # Load macro data
    macro_file = project_root / "data" / "macro" / "cpi.csv"
    surprise_df = surprise_engine.build_surprise_series(macro_file)

    latest_event = surprise_df.iloc[-1]

    event_time = pd.Timestamp(
        f"{latest_event['date'].date()} 08:30",
        tz="US/Eastern"
    )

    assets = loader.load_all_assets()

    start = (event_time - pd.Timedelta(days=20)).strftime("%Y-%m-%d")
    end = (event_time + pd.Timedelta(days=20)).strftime("%Y-%m-%d")

    reaction_results = {}

    for group, asset in assets.items():

        if isinstance(asset, list):
            iterable = asset
        else:
            iterable = [asset]

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

            reaction_results[item["name"]] = reactions

    summary = transmission_engine.summarize_event(reaction_results)

    report = f"""
MACRO EVENT REPORT
==================
Date: {latest_event['date'].date()}
Surprise Z-Score: {round(latest_event['surprise_z'],2)}

Lead Asset: {summary['lead_asset']}
Transmission Strength: {round(summary['transmission_strength'],2)}

Event Matrix:
{summary['event_matrix']}
"""

    output_file = project_root / "outputs" / "reports" / "latest_report.txt"

    with open(output_file, "w") as f:
        f.write(report)

    print("Report generated:", output_file)


if __name__ == "__main__":
    generate_macro_report(project_root)