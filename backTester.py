import decimal
import queue
from dataHandler import csvData
from events import event as event_class
from optionPrimitives import optionPrimitive
from riskManagement import strangleRiskManagement
from strategyManager import strategy, strangleStrat
from portfolioManager import portfolio
from datetime import datetime
import pytz
import logging

"""
This file contains a basic strategy example, and can be thought of 
as an end-to-end test of the whole Backtester project.
In this example, we actually backtest a strategy and do not use
the suite for live trading.  Live trading is currently not supported.
"""

class BackTestSession(object):
  """Class for holding all parameters of backtesting session."""

  def __init__(self):
    # Create queue to hold events (ticks, signals, etc.).
    self.eventQueue = queue.Queue()

    # Create CsvData class object.
    # TODO: this is too slow; let's break up the files by week maybe and load a directory?
    dataProvider = 'iVolatility'
    filename = '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/combinedCSV.csv'
    self.dataHandler = csvData.CsvData(csvPath=filename, dataProvider=dataProvider, eventQueue=self.eventQueue)

    # Parameters for strangle strategy -- TODO: move params to file.
    optCallDelta = 0.16
    maxCallDelta = 0.30
    optPutDelta = -0.16
    maxPutDelta = -0.30
    startDateTime = datetime.now(pytz.utc)
    buyOrSell = optionPrimitive.TransactionType.SELL
    underlyingTicker = 'SPX'
    orderQuantity = 1
    expCycle = strategy.ExpirationTypes.MONTHLY
    optimalDTE = 45
    minimumDTE = 25
    minCredit = 0.5
    maxBidAsk = 15 # A general rule of thumb is to take 0.001*underlyingPrice.  Set to 15 to mostly ignore field.
    startingCapital = decimal.Decimal(1000000)
    maxCapitalToUse = 0.5  # Up to 50% of net liq can be used in trades.
    maxCapitalToUsePerTrade = 0.10  # 10% max capital to use per trade / strategy.
    minBuyingPower = decimal.Decimal(maxCapitalToUsePerTrade)*startingCapital

    # Set up strategy (strangle strategy) and risk management preference.
    riskManagement = strangleRiskManagement.StrangleRiskManagement(
      strangleRiskManagement.StrangleManagementStrategyTypes.HOLD_TO_EXPIRATION)
    self.strategyManager = strangleStrat.StrangleStrat(self.eventQueue, optCallDelta, maxCallDelta, optPutDelta,
                                                       maxPutDelta, startDateTime, buyOrSell, underlyingTicker,
                                                       orderQuantity, riskManagement, expCycle, optimalDTE,
                                                       minimumDTE, minCredit=minCredit, maxBidAsk=maxBidAsk,
                                                       minBuyingPower=minBuyingPower)
    # Set up portfolio.
    self.portfolioManager = portfolio.Portfolio(startingCapital, maxCapitalToUse, maxCapitalToUsePerTrade)

def run(session):
  while (1):  #Infinite loop to keep processing items in queue.
    # print('Trying another...')
    try:
      event = session.eventQueue.get(False)
    except queue.Empty:
      #Get data for tick event.
      # print('try getting data.')
      if not session.dataHandler.getNextTick():
        # Get out of infinite while loop; no more data available.
        break
      # print('got data.')
    else:
      if event is not None:
        if event.type == event_class.EventTypes.TICK:
          #self.cur_time = event.time
          session.strategyManager.checkForSignal(event)
          session.portfolioManager.updatePortfolio(event)
          # Update the buying power that can now be used for the strategy, but only if minBuyingPower is not
          # set to None.
          # if session.minBuyingPower:
          #     session.strategyManager.setMinBuyingPower(session.maxCapitalToUsePerTrade*netLiq)
        elif event.type == event_class.EventTypes.SIGNAL:
          session.portfolioManager.onSignal(event)
        else:
          raise NotImplemented("Unsupported event.type '%s'." % event.type)

if __name__ == "__main__":
  # Set up logging for the session.
  logging.basicConfig(filename='session.log', level=logging.FATAL) #level=logging.DEBUG)

  # Create a session and configure the session.
  session = BackTestSession()

  # Run the session.
  run(session)