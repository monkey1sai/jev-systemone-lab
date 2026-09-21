# -*- coding: utf-8 -*-
"""The other half of the skeleton: typed functions -> one request -> a call."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from typing import Literal
from jev import Client, Dispatcher

def plot_price(symbol: Literal["SPY","NVDA","AMD","AAPL","MSFT","TSLA"],
               style: Literal["line","candles"] = "line",
               window: Literal["1d","1w","1mo","3mo"] = "1w",
               include_volume: bool = False,
               limit: int = 3):
    return f"chart {symbol} {style} {window} volume={include_volume} limit={limit}"

def compare_returns(symbols: list[Literal["SPY","NVDA","AMD","AAPL","MSFT","TSLA"]],
                    window: Literal["1d","1w","1mo","3mo"] = "1w"):
    return f"compare {symbols} over {window}"

def list_symbols():
    return "SPY NVDA AMD AAPL MSFT TSLA"

TOOLS = {f.__name__: f for f in (plot_price, compare_returns, list_symbols)}
TICKERS = {t: f"the ticker {t}" for t in ("SPY","NVDA","AMD","AAPL","MSFT","TSLA")}
WINDOW = {"1d":"a single day","1w":"about a week","1mo":"about a month","3mo":"about a quarter"}

SPEC = {
 "route": "What is the user asking the trading assistant to do?",
 "functions": {
  "plot_price": {"description": "draw the price of one ticker over time",
   "arguments": {
     "symbol": {"question": "Which company's price is being asked about?", "options": TICKERS},
     "style":  {"question": "Does the user want a plain line or candles?",
                "stated": "Does the user say how the chart should be drawn, such as a line, candles or OHLC bars?",
                "options": {"line":"a simple line through the closing prices",
                            "candles":"a candlestick or OHLC chart showing open, high, low and close"}},
     "window": {"question": "How far back should the chart reach?",
                "stated": "Does the user say how far back to look?", "options": WINDOW},
     "include_volume": {"question": "Does the user want traded volume shown as well?"}}},
  "compare_returns": {"description": "compare the returns of several tickers against each other",
   "arguments": {
     "symbols": {"question": "Does the user want {} included in the comparison?", "options": TICKERS},
     "window": {"question": "Over what period should they be compared?",
                "stated": "Does the user say over what period?", "options": WINDOW}}},
  "list_symbols": {"description": "say which tickers are available at all", "arguments": {}}}}

d = Dispatcher(SPEC, TOOLS, Client())
print(f"  {len(d.questions)} questions built from {len(TOOLS)} functions\n")
for cmd in ("candles for tesla with volume over the past month",
            "compare nvda amd and msft",
            "what tickers do you have",
            "show me apple"):
    call = d(cmd)
    print(f'  "{cmd}"')
    print(f"      {str(call):<62} confidence {call.confidence:.2f}  {call.ms}ms")
    for a in call.arguments.values():
        shown = "omitted, default stands" if a.omitted else repr(a.value)
        print(f"        {a.name:<16}{shown:<28}p {a.probability:.2f}")
    w = call.weakest()
    if w: print(f"        weakest: {w.name}")
    print(f"        run() -> {call.run()}\n")
