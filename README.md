📊 Macro Transmission Engine
An event-study based analytics platform that studies how macroeconomic surprises transmit across financial markets.

This project focuses on understanding market behaviour, not price prediction.
It measures how different asset classes react to economic information shocks such as inflation releases.

🚀 Motivation
Financial markets continuously price macroeconomic information.

Key questions macro strategists ask:

Which asset reacts first to macro news?
How strong is cross-asset transmission?
Are reactions persistent or noisy?
Was the market move statistically unusual?
This project builds a research framework to empirically study these dynamics using historical data.

🧠 Methodology
The system follows a structured macro event study workflow:

Construct macro surprise series

CPI actual vs expectation proxy
Normalize shocks using rolling volatility
Compute surprise z-scores
Measure cross-asset reactions

Equity proxy (SPY ETF)
Short-duration bonds (SHY ETF)
Long-duration bonds (IEF ETF)
Dollar index proxy
Volatility index (VIX)
Build transmission matrix

Reaction across multiple time horizons
Identify lead asset
Compute transmission persistence
Perform historical analytics

Reaction distributions
Shock sensitivity regression
Event-by-event comparison
📈 Dashboard Features
The Streamlit dashboard provides an interactive research interface:

Historical CPI surprise time series
Event selector for macro releases
Cross-asset reaction visualization
Transmission matrix table
Lead asset detection
Transmission strength indicator
Reaction distribution analysis
Shock sensitivity scatter plot
This allows users to explore how macro shocks propagate through markets.

🛠 Tech Stack
Python
Pandas / NumPy
Matplotlib
Streamlit
Yahoo Finance data (daily resolution)
⚠️ Data Notes
CPI actual values sourced from official macro datasets (FRED/BLS).
Consensus expectations approximated using lagged inflation prints.
Market reactions measured using daily price data due to historical intraday availability constraints.
The framework is designed to be extendable to higher-frequency datasets.

📊 Example Insight
Empirical analysis shows that inflation surprises tend to transmit primarily through duration-sensitive assets, while equity reactions are more regime-dependent.

This aligns with macro theory where interest rate expectations act as the primary pricing channel.

🔮 Future Improvements
Intraday event study using higher-frequency data
Additional macro events (NFP, FOMC decisions, PMI)
Regime detection and conditional sensitivity analysis
Portfolio-level transmission analytics
🎯 Purpose
This project demonstrates:

macroeconomic intuition
quantitative event-study modelling
financial data engineering
interactive analytics dashboard design
It is intended as a research prototype for understanding information flow in financial markets.

📷 Dashboard Preview
