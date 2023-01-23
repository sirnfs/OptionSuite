import csv
import datetime
import decimal
import logging
import queue
from dataHandler import csvData
from events import event as event_class
from optionPrimitives import optionPrimitive
from riskManagement import putVerticalRiskManagement, strangleRiskManagement
from strategyManager import strategy, StrangleStrat, putVerticalOnDownMoveStrat
from portfolioManager import portfolio
from datetime import datetime
from collections import defaultdict

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
    dataProvider = 'iVolatility'
    filename = '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/combinedCSV.csv'
    self.dataHandler = csvData.CsvData(csvPath=filename, dataProvider=dataProvider, eventQueue=self.eventQueue)

    # Parameters for strangle strategy -- TODO: move params to file.
    optCallDelta = 0.16
    maxCallDelta = 0.30
    optPutDelta = -0.16
    maxPutDelta = -0.30
    startDateTime = None
    buyOrSell = optionPrimitive.TransactionType.SELL
    underlyingTicker = 'SPX'
    orderQuantity = 1
    expCycle = strategy.ExpirationTypes.MONTHLY
    optimalDTE = 45
    minimumDTE = 35
    maxBidAsk = 15 # A general rule of thumb is to take 0.001*underlyingPrice.  Set to 15 to ignore field.
    startingCapital = decimal.Decimal(200000)
    self.maxCapitalToUse = 0.5  # Up to 50% of net liq can be used in trades.
    maxCapitalToUsePerTrade = 0.10  # 10% max capital to use per trade / strategy.
    # Set up strategy (strangle strategy) and risk management preference.
    riskManagement = strangleRiskManagement.StrangleRiskManagement(
      strangleRiskManagement.StrangleManagementStrategyTypes.CLOSE_AT_50_PERCENT)  # strangleRiskManagement.StrangleManagementStrategyTypes.HOLD_TO_EXPIRATION)
    self.strategyManager = StrangleStrat.StrangleStrat(self.eventQueue, optCallDelta, maxCallDelta, optPutDelta,
                                                       maxPutDelta, buyOrSell, underlyingTicker,
                                                       orderQuantity, riskManagement, expCycle, optimalDTE,
                                                       minimumDTE, maxBidAsk=maxBidAsk,
                                                       maxCapitalToUsePerTrade=maxCapitalToUsePerTrade,
                                                       startDateTime=startDateTime)

    # Set up portfolio.
    # Dictionary used to keep track of portfolio value changes.
    self.positionMonitoring = defaultdict(list)
    pricingSource = 'tastyworks'
    pricingSourceConfigFile = './dataHandler/pricingConfig.json'
    self.portfolioManager = portfolio.Portfolio(startingCapital, self.maxCapitalToUse, maxCapitalToUsePerTrade,
                                                positionMonitoring=self.positionMonitoring,
                                                pricingSource=pricingSource,
                                                pricingSourceConfigFile=pricingSourceConfigFile)
    # Write params to log file to be able to track experiments.
    logging.info(
      'optCallDelta: {} maxCallDelta: {} optPutDelta: {} maxPutDelta: {} startDateTime: {} underlyingTicker: {} orderQuantity: {} expCycle: {} optimalDTE: {} minimumDTE: {} maxBidAsk: {} riskManagement: {} startingCapital: {} self.maxCapitalToUse: {} maxCapitalToUsePerTrade: {} pricingSource: {}'.format(
        optCallDelta, maxCallDelta, optPutDelta, maxPutDelta, startDateTime, underlyingTicker, orderQuantity, expCycle,
        optimalDTE, minimumDTE, maxBidAsk, riskManagement.getRiskManagementType(), startingCapital,
        self.maxCapitalToUse, maxCapitalToUsePerTrade, pricingSource))

    # Parameters for put vertical strategy -- TODO: move params to file.
    # optPutToSellDelta = -0.16
    # maxPutToSellDelta = -0.20
    # minPutToSellDelta = -0.12
    # optPutToBuyDelta = -0.10
    # maxPutToBuyDelta = -0.14
    # minPutToBuyDelta = -0.06
    # startDateTime = None  # datetime.strptime('01/01/2005', '%m/%d/%Y')
    # underlyingTicker = 'SPX'
    # orderQuantity = 1
    # expCycle = strategy.ExpirationTypes.MONTHLY
    # optimalDTE =  45
    # minimumDTE = 35
    # maxBidAsk = 15  # A general rule of thumb is to take 0.001*underlyingPrice.  Set to 15 to ignore field.
    # percentDownToTrigger = -0.01
    # numberDaysForMovingAverage = 0
    # riskManagement = putVerticalRiskManagement.PutVerticalRiskManagement(
    #   putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT)
    # startingCapital = decimal.Decimal(200000)
    # self.maxCapitalToUse = 0.5  # Up to 50% of net liq can be used in trades.
    # maxCapitalToUsePerTrade = 0.10  # 10% max capital to use per trade / strategy.
    # self.strategyManager = putVerticalOnDownMoveStrat.PutVerticalOnDownMoveStrat(
    #   self.eventQueue, percentDownToTrigger, numberDaysForMovingAverage, optPutToBuyDelta, maxPutToBuyDelta,
    #   minPutToBuyDelta, optPutToSellDelta, maxPutToSellDelta, minPutToSellDelta, underlyingTicker, orderQuantity,
    #   riskManagement, expCycle, optimalDTE, minimumDTE, maxBidAsk=maxBidAsk,
    #   maxCapitalToUsePerTrade=maxCapitalToUsePerTrade, startDateTime=startDateTime)

    # Set up portfolio.
    # Dictionary used to keep track of portfolio value changes.
    # self.positionMonitoring = defaultdict(list)
    # pricingSource = 'tastyworks'
    # pricingSourceConfigFile = './dataHandler/pricingConfig.json'
    # self.portfolioManager = portfolio.Portfolio(startingCapital, self.maxCapitalToUse, maxCapitalToUsePerTrade,
    #                                             positionMonitoring=self.positionMonitoring,
    #                                             pricingSource=pricingSource,
    #                                             pricingSourceConfigFile=pricingSourceConfigFile)
    # # Write params to log file to be able to track experiments.
    # logging.info('optPutToSellDelta: {}  maxPutToSellDelta: {} minPutToSellDelta: {} optPutToBuyDelta: {} maxPutToBuyDelta: {} minPutToBuyDelta: {} startDateTime: {} underlyingTicker: {} orderQuantity: {} expCycle: {} optimalDTE: {} minimumDTE: {} maxBidAsk: {} percentDownToTrigger: {} numberDaysForMovingAverage: {} riskManagement: {} startingCapital: {} self.maxCapitalToUse: {} maxCapitalToUsePerTrade: {} pricingSource: {}'.format(
    #                optPutToSellDelta, maxPutToSellDelta, minPutToSellDelta, optPutToBuyDelta, maxPutToBuyDelta,
    #                minPutToBuyDelta, startDateTime, underlyingTicker, orderQuantity, expCycle, optimalDTE, minimumDTE,
    #                maxBidAsk, percentDownToTrigger, numberDaysForMovingAverage, riskManagement.getRiskManagementType(),
    #                startingCapital, self.maxCapitalToUse, maxCapitalToUsePerTrade, pricingSource))

def run(session):
  while (1):  #Infinite loop to keep processing items in queue.
    try:
      event = session.eventQueue.get(False)
    except queue.Empty:
      #Get data for tick event.
      if not session.dataHandler.getNextTick():
        # Get out of infinite while loop; no more data available.
        break
    else:
      if event is not None:
        if event.type == event_class.EventTypes.TICK:
          session.portfolioManager.updatePortfolio(event)
          # We pass the net liquidity and available buying power to the strategy.
          availableBuyingPower = decimal.Decimal(
            session.maxCapitalToUse)*session.portfolioManager.netLiquidity - session.portfolioManager.totalBuyingPower
          session.strategyManager.checkForSignal(event, session.portfolioManager.netLiquidity, availableBuyingPower)
        elif event.type == event_class.EventTypes.SIGNAL:
          session.portfolioManager.onSignal(event)
        else:
          raise NotImplemented("Unsupported event.type '%s'." % event.type)

if __name__ == "__main__":

  # Set up basename for output files.
  baseName = 'positions_strangle_01_15_21'

  # Set up logging for the session.
  logging.basicConfig(filename=baseName+'.log', level=logging.DEBUG)

  # Create a session and configure the session.
  session = BackTestSession()

  # Run the session.
  run(session)

  # Write position monitoring to CSV file.
  with open(baseName + '.csv', 'w') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(session.positionMonitoring.keys())
    writer.writerows(zip(*session.positionMonitoring.values()))
