import pandas as pd
import numpy as np


class RegimeEngine:

    def __init__(self, correlation_window_days, break_threshold):

        self.correlation_window_days = correlation_window_days
        self.break_threshold = break_threshold

    # -------------------------
    # Rolling Correlation
    # -------------------------

    def compute_rolling_correlation(
        self,
        df,
        asset_x,
        asset_y
    ):

        corr = (
            df[asset_x]
            .rolling(self.correlation_window_days)
            .corr(df[asset_y])
        )

        return corr

    # -------------------------
    # Z-score
    # -------------------------

    def correlation_zscore(self, corr_series):

        mean = corr_series.mean()
        std = corr_series.std()

        return (corr_series - mean) / std

    # -------------------------
    # Regime Classification
    # -------------------------

    def classify_regime(self, corr_series):

        z = self.correlation_zscore(corr_series)

        regime = pd.Series("Normal", index=corr_series.index)

        regime[z > self.break_threshold] = "Risk-On CoMove"
        regime[z < -self.break_threshold] = "Diversification Break"
        regime[z.abs() > self.break_threshold] = "Stress"

        return pd.DataFrame({
            "correlation": corr_series,
            "z_score": z,
            "regime": regime
        })

    # -------------------------
    # Quick Stress Signal
    # -------------------------

    def stress_signal(self, regime_df):

        latest = regime_df.iloc[-1]

        if latest["regime"] == "Stress":
            return 1
        return 0