import pandas as pd
import numpy as np


class MacroSurpriseEngine:
    """
    Computes normalized macroeconomic surprises.

    Surprise logic:
        surprise = actual - forecast
        normalized_surprise = surprise / rolling_std(surprise)

    This reflects how markets react to deviations from expectations,
    not the absolute level of macro data.
    """

    def __init__(self, surprise_vol_window: int = 24):
        """
        Parameters
        ----------
        surprise_vol_window : int
            Number of past events used to estimate surprise volatility.
        """
        self.surprise_vol_window = surprise_vol_window

    def load_macro_data(self, filepath: str) -> pd.DataFrame:
        """
        Load macroeconomic event data.

        Expected columns:
        - date
        - event
        - actual
        - forecast

        Returns
        -------
        pd.DataFrame
        """
        df = pd.read_csv(filepath)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        return df

    def compute_surprise(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute raw macro surprise (actual - forecast).

        Returns
        -------
        pd.DataFrame
        """
        df = df.copy()
        df["surprise"] = df["actual"] - df["forecast"]
        return df

    def normalize_surprise(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize macro surprise using rolling standard deviation.

        Returns
        -------
        pd.DataFrame
        """
        df = df.copy()

        df["surprise_vol"] = (
            df["surprise"]
            .rolling(self.surprise_vol_window, min_periods=5)
            .std()
        )

        df["surprise_z"] = df["surprise"] / df["surprise_vol"]

        return df

    def build_surprise_series(self, filepath: str) -> pd.DataFrame:
        """
        Full pipeline:
        Load data -> compute surprise -> normalize

        Returns
        -------
        pd.DataFrame
        """
        df = self.load_macro_data(filepath)
        df = self.compute_surprise(df)
        df = self.normalize_surprise(df)
        return df
