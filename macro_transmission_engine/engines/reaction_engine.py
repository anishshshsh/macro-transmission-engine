import pandas as pd
import numpy as np


class MarketReactionEngine:
    """
    Computes market reactions to macro events across multiple time windows.
    """

    def __init__(self, event_windows, pre_event_window):
        self.event_windows = event_windows
        self.pre_event_window = pre_event_window

    def compute_reactions(self, df, event_time, asset_type):

        reactions = {}

        # ---------- basic safety
        if df is None:
            return reactions

        if len(df) == 0:
            return reactions

        df = df.copy()

        # ---------- enforce datetime column
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            time_col = "Date"
        elif "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"])
            time_col = "datetime"
        else:
            return reactions

        # ---------- enforce price column
        if "price" not in df.columns:
            return reactions

        df = df.sort_values(time_col)

        # ---------- baseline = last price BEFORE event
        baseline_df = df[df[time_col] <= event_time]

        if len(baseline_df) == 0:
            return reactions

        baseline_price = baseline_df.iloc[-1]["price"]

        try:
            baseline_price = float(baseline_price)
        except:
            return reactions

        if baseline_price == 0:
            return reactions

        # ---------- compute reactions
        for window in self.event_windows:

            horizon = event_time + pd.Timedelta(minutes=window)

            future_df = df[df[time_col] >= horizon]

            if len(future_df) == 0:
                continue

            reaction_price = future_df.iloc[0]["price"]

            try:
                reaction_price = float(reaction_price)
            except:
                continue

            reaction = (reaction_price - baseline_price) / baseline_price

            reactions[str(window) + "m"] = reaction

        return reactions