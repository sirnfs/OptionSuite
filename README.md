# OptionSuite
Options strategy backtester and live trader* framework

# Objective
The objective of the OptionSuite library is to create a general framework to backtest options strategies and to be extensible enough to handle live trading.

*Live trader is currently not supported, but the general framework is in place to expand support for live trading.

# Overview
The library is designed in a modular way, and several abstractions are provided which allow the user to add additional features.  The structure of the library is as follows:

base

dataHandler

events	

optionPrimitives	

portfolioManager	

sampleData	

strategyManager	

utils
