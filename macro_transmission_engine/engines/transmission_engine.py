import pandas as pd
import numpy as np


class TransmissionEngine:
    """
    Analyzes cross-asset transmission of macro shocks.
    """

    def __init__(self, event_windows):
        self.event_windows = event_windows

    # ---------------- MATRIX BUILDER ----------------
    def build_event_matrix(self, reaction_data: dict) -> pd.DataFrame:

        if not reaction_data:
            return pd.DataFrame()

        df = pd.DataFrame(reaction_data).T

        if df.empty:
            return df

        df = df[self._ordered_columns(df)]

        return df

    def _ordered_columns(self, df: pd.DataFrame):

        cols = list(df.columns)

        try:
            cols_sorted = sorted(cols, key=lambda x: int(str(x).replace("m", "")))
        except:
            cols_sorted = cols

        return cols_sorted

    # ---------------- LEAD ASSET ----------------
    def detect_lead_asset(self, event_matrix: pd.DataFrame) -> str:

        if event_matrix is None:
            return "No valid reactions"

        if event_matrix.empty:
            return "No valid reactions"

        if len(event_matrix.columns) == 0:
            return "No valid reactions"

        first_window = event_matrix.columns[0]

        try:
            lead_asset = event_matrix[first_window].abs().idxmax()
            return lead_asset
        except:
            return "No valid reactions"

    # ---------------- TRANSMISSION STRENGTH ----------------
    def compute_transmission_strength(self, event_matrix: pd.DataFrame) -> float:
        """
        Measures whether reactions build / persist across horizons.
        """

        if event_matrix is None:
            return 0

        if event_matrix.empty:
            return 0

        strengths = []

        for asset in event_matrix.index:

            series = event_matrix.loc[asset].dropna()

            if len(series) < 2:
                continue

            try:
                monotonic = np.all(np.diff(np.abs(series)) >= 0)
                strengths.append(1.0 if monotonic else 0.0)
            except:
                continue

        if len(strengths) == 0:
            return 0

        return float(np.mean(strengths))

    # ---------------- EVENT SUMMARY ----------------
    def summarize_event(self, reaction_results):

        if not reaction_results:
            return {
                "event_matrix": pd.DataFrame(),
                "lead_asset": "No valid reactions",
                "transmission_strength": 0
            }

        event_matrix = self.build_event_matrix(reaction_results)

        if event_matrix.empty:
            return {
                "event_matrix": pd.DataFrame(),
                "lead_asset": "No valid reactions",
                "transmission_strength": 0
            }

        lead_asset = self.detect_lead_asset(event_matrix)

        strength = self.compute_transmission_strength(event_matrix)

        return {
            "event_matrix": event_matrix,
            "lead_asset": lead_asset,
            "transmission_strength": strength
        }