"""
Sample prompt templates and background knowledge used as system prompts
for LLMs in this project.

This module exports BACKGROUND_KNOWLEDGE, ANALYSIS_INSTRUCTIONS, and
NARRATIVE_INSTRUCTIONS (combined).
"""

__all__ = ["BACKGROUND_KNOWLEDGE", "ANALYSIS_INSTRUCTIONS", "NARRATIVE_INSTRUCTIONS"]

BACKGROUND_KNOWLEDGE = '''
Title: Header definitions of  data and chart data:

Daily chart use Fibonacci based on previous week. Moving average lines are EMA 50, 100, and 200. Notice the volume divergence of the previous two three days.  The hourly chart, for SPX, instead of SPY, use Fibonacci Pivot based on previous day. The 15 minute chart is for SPY, use Fibonacci Pivot based on previous week. FIN INSTR - Financial Instrument

HV CLOSE: 30-day historical volatility based of previous close
13 WEEK HV RANK, 26HVR, and 52HVR: 13-, 26, AND 52-week ranking of 30-day historical volatility
13HVP, 26HVP, and 52HVP: 13-, 26-, and 52-week percentile of 30-day historical volatility
OPT.IMPLD VLTLTY %: 30-day implied volatility of the instrument based on at-the-money options
OPT.IMP.VL.CHNG: absolute change of implied volatility between current and previous close
13IVR, 26IVR, and 52IVR: 13-, 26-, and 52-week implied volatility Rank
13IVP, 26IVP, and 52IVP: 13-, 26-, and 52-week implied volatility Percentile
13 WEEK HIGH, 26 WEEK HIGH, and 52WK HIGH: 13-, 26-, and 52-week highest price of the instrument
13 WK LW, 26 WEEK LOW, and 52WK LW: 13-, 26-, and 52-week lowest price of the instrument
GRPHC CHNG: graphic indication for human eyes
SMART SPINNER: graphic indication for human eyes
CANDLESTICK: graphic indication for human eyes
RNG: graphic indication for human eyes
LAST: market price of the instrument
CHANGE: absolute change of the market price of instrument from previous close
CHNG %: percentage change of the market price of instrument from previous close
MTD%: month-to-date percentage change of instrument price
FWD P/E: last close price of the instrument divided by rolling 12-month earning-per-share forecast

Title: Augmented knowledge points and definitions, in case your training does not include them:

Contango of VIX term structure is normal for a stable and bullish stock market.

Contango of rates term structure is normal.

VVIX is an index of VIX options metrics, including volatility consideration.

USD is a Forex pair of Japanese Yen.

VOLI® uses at-the-money options of the ETF SPY, the most important options for market participants, the number measures the implied volatility of a hypothetical precisely at-the-money SPY (SPDR S&P 500 ETF) option with precisely 30 days to expiration. VOLI identifies the weekly SPY option expirations bracketing 30 days from the current minute then incorporates the first call and put option above and below the forward price in each of those expirations. Those at-the-money options are then interpolated into a single mathematically robust, closed-form measure of implied volatility.

TailDex® (ticker TDEX) measures the cost of deep out-of-the-money SPY puts, it calculates the normalized price of a put option that is three standard deviations away from the current price of SPY.

SkewDex® (ticker SDEX) defines the amount of put skew in the SPY option market, it measures the difference in implied volatility (IV) between at-the-money (ATM) and one standard deviation out-of-the-money (OTM) put options on SPY.

VXM is a continuous future contract on VIX. Due to its rolling nature, it is always the contract that expires end of the current month.

Some indices such VIX3M and VVIX do not seems to have exchange trade options, nor do they have historical volatility. This is acceptable.

FVX, TNX, TYX tracks the yield on the 5-year, 10-year, and 30-year US Treasury note/bond.
'''


ANALYSIS_INSTRUCTIONS = '''
Base on the snapshot market data related to instrument risks, and optionally the associated charts, please perform a detailed market analysis adhering to the following instructions:

Please do the following:

1. Put conclusion upfront.
2. Analyze each item in detail.
3. Always take a historical perspective, using background data of 13-, 26-, and 52 week rankings below.
4. Do not omit any data or leave it excluded from analysis.
5. Identify potential correlations between metrics.
6. Generate a coherent market narrative based on the data.
7. Identify breakdown of correlations and/or anomalies.
8. Incorporate analysis of economic indicators.
9. Indicate what data are missing to form a complete picture.
10. Indicate what instruments such as symbol or description you do not understand because of lack of training.
'''

NARRATIVE_INSTRUCTIONS = BACKGROUND_KNOWLEDGE + "\n\n" + ANALYSIS_INSTRUCTIONS
# from typing import Optional, Union, List, Dict

"""Settings for market data retrieval."""

PREDEFINED_WATCHLIST_SYMBOLS = [
    "VVIX",
    "VIX",
    "VXM",
    "MBT",
    "MES",
    "MCL",
    "MGC",
    "USD.JPY",
    "SPX",
    "SPY",
    "RSP",
    "DIA",
    "QQQ",
    "IWM",
    "HSI",
    "FXI",
    "XINA50",
    "N225",
    "XAGUSD",
    "DX",
    "FVX",
    "TNX",
    "TYX",
    "VOLI",
    "SDEX",
    "TDEX",
    "VIX1D",
    "VIX9D",
    "VIX3M",
    "VIX6M",
    "VIX1Y"
]
DEFAULT_FIELDS = ['55','7051','7635','31','70','71','7295','7741', '7293','7294', '7681', '7724', '7679', '7678','7283', '7087']
# IBKR market data field mappings
