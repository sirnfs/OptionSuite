# OptionSuite
Option / stock strategy backtester and live trader* framework.

To get started quickly, click the image below to bring up the tutorial video on YouTube.

[![Video Tutorial](https://img.youtube.com/vi/gvzlKoPj57A/0.jpg)](https://www.youtube.com/watch?v=gvzlKoPj57A)

# Looking for a winning strategy developed by this backtester? Check out [IncreaseYourStockReturns](https://www.increaseyourstockreturns.com/)!

# Press / tutorials by others:

[Pipkekit](https://pipekit.io/blog/options-backtesting-in-python-an-introductory-walkthrough)

[Medium](https://medium.com/coinmonks/options-backtesting-in-python-an-introductory-walkthrough-fa14b32642ef)


[Getting started](#getting-started) decribes what you need in order to get started backtesting.

Please note that you need to purchase a [data package](#getting-the-data) in order to use this library since the sample data is quite limited.

# Objective
The objective of the OptionSuite library is to create a general framework to backtest options strategies and to be extensible enough to handle live trading.

*Live trader is currently not supported, but the general framework is in place to enable support for live trading.

# Overview of Library
The library is designed in a modular way, and several abstractions are provided which allow the user to add additional features.  The directory structure of the library is as follows:

**base** - contains the abstract options class (option.py) and the two derived classes (call.py and put.py), which serve as the general options types for all other classes.

**dataHandler** - contains the abstract class (dataHandler.py), which is set up to handle loading option data from different sources.  The framework has been tested with CSV data, and a CSV data handler class (csvData.py) is provided to load tick data provided through the CSV format.  An example CSV format is provided in the **sampleData** directory.  More information on the CSV data needed for back testing is covered in the [getting started](#getting-started) section.

**events** - the entire library / framework is event driven, and the abstract event class (event.py) handles the creation and deletion of events.  The framework currently supports two different types of events:  tick events (tickEvent.py) and signal events (signalEvent.py).  The tick events are used to load data from the **dataHandler** and create the base option types (puts and calls).  Signal events are generated to indicate that the criteria for the strategy in **strategyManager** has been successfully met. 

**optionPrimitives**	- option primitives allow for naked puts and calls as well as combinations of puts and calls.  For example, an option primtive could describe a naked put, or it could describe a strangle, which is a combination of puts and calls.  Since certain trades like strangles are common, the option primitives abstract class (optionPrimitive.py) wraps the base types (calls and puts), and describes the functionality needed to create and update the primitive.  The strangle primitive (strangle.py) and put vertical (putVertical.py) are fully functional.   

**portfolioManager** - the portfolio manager (portfolio.py) holds and manages all of the open positions.  Potential positions are first generated by the **strategyManager**, and the portfolio manager opens a new positions if all risk paramters have been met.  The portfolio is current held in memory, but a future implementation would ideally store the positions into a database or other non-volatile source.	

**sampleData** - a single file spx_sample_ivolatility.csv is provided.  It serves as an example of the CSV data format provided by iVolatility.	

**strategyManager** - the strategy manager module provides an abstract class (strategy.py) which defines the basic parameters needed for an options strategy.  The purpose of the strategy manager module is to filter the incoming tick data (by means of a tick event) to determine if a position should be opened (which would in turn fire a signal event).  A full strangle stategy (StrangleStrat.py) and put vertical strategy (putVerticalStrat.py) are provided, which includes options for trade management as well as several different criteria for determining if a trade should be opened (signal event generated).

**utils** - the utilities directory provides a utility for combining CSVs (e.g., if there are multiple CSVs for different years of historical data). 

**backTester.py** - this is the "main" method for the library.  It sets up all parameters for a backtesting session, and initializes the **dataHandler** class, the **portfolioManager** class, and the **strategyManager** class.  It is helpful to start with this file to see how all of the modules work together.

# Getting Started 
*The library has been tested with Python 2.7+*

To get started, you first need some historical data for the backtests.  

## Getting the Data

The *combinedCSV.csv* file used during development and testing contains SPX data from 1990 to 2017 provided by [iVolatility](http://www.ivolatility.com/fast_data_sales_form1.j).  If you'd like to use the same dataset I did, then you want to request the EOD Raw IV dataset for SPX. 

*There is a 10% discount on all orders greater than $100 if you use code SupraCV10PCTOFF in the "Please tell us what data you want to receive:" field.*

You can request different time periods.  A large time period such as 1990 to 2017 is broken up into multiple CSVs.  The *combineCSVs.py* in **utils** can be used to combine multiple CSVs into a single CSV.

## Loading the Data

Once you have downloaded the data, simply update the three lines below, and you are ready to run *backTester.py*.

```
dataProviderPath = '/Users/msantoro/PycharmProjects/Backtester/dataHandler/dataProviders.json'
dataProvider = 'iVolatility'
filename = '/Users/msantoro/PycharmProjects/Backtester/sampleData/spx_sample_ivolatility.csv'
```

## Visualizing the Data

The output data is written to CSV in the *monitoring.csv* file.

# Troubleshooting
Please send bugs or any other issues you encounter to [msantoro@gmail.com](mailto:msantoro@gmail.com).  I will do my best to help you get up and running.  You can also report an issue using GitHub's issue tracker.

