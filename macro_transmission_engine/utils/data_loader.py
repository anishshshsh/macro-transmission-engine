import yaml
import pandas as pd
from pathlib import Path
import yfinance as yf


class DataLoader:

    def __init__(self, project_root):

        self.project_root = Path(project_root)
        self.config_path = self.project_root / "config"
        self.data_path = self.project_root / "data"

        self.settings = self._load_yaml("settings.yaml")
        self.assets = self._load_yaml("assets.yaml")

    # -------------------------
    # CONFIG
    # -------------------------

    def _load_yaml(self, filename):

        with open(self.config_path / filename, "r") as f:
            return yaml.safe_load(f)

    def get_event_windows(self):
        return self.settings["event_windows"]

    def get_pre_event_window(self):
        return self.settings["pre_event_window"]

    # -------------------------
    # MACRO DATA
    # -------------------------

    def load_macro_file(self, filename):

        df = pd.read_csv(self.data_path / "macro" / filename)

        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        return df.reset_index(drop=True)

    # -------------------------
    # MARKET DATA
    # -------------------------

    def fetch_market_data(self, ticker, start, end):

        df = yf.download(
            ticker,
            start=start,
            end=end,
            progress=False
        )

        if df.empty:
            raise ValueError(f"No data returned for {ticker}")

        # Flatten MultiIndex if exists
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()

        # Use Close as price
        df = df.rename(columns={
            "Date": "datetime",
            "Close": "price"
        })

        df["datetime"] = pd.to_datetime(df["datetime"]).dt.tz_localize("US/Eastern")

        return df[["datetime", "price"]]

    def load_all_assets(self):
        return self.assets