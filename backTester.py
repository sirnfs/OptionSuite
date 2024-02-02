import csv
import datetime
import decimal
import logging
import queue
from dataHandler import csvData
from events import event as event_class
from riskManager import putVerticalRiskManagement, shortNakedPutRiskManagement
from strategyManager import strategy, putVerticalOnDownMoveStrat, nakedPutStrat
from portfolioManager import portfolio
from collections import defaultdict

"""
This file runs the end-to-end backtesting session. It also supports multi-run sweeps. Configuration for the session
is loaded through YAML files in sweepConfig.
"""

class BackTestSession(object):
  """Class for holding all parameters of backtesting session.

    Attributes:
      configStrategy: hydra YAML dictionary configuration with strategy parameters.
  """
  def __init__(self):

    # Create queue to hold events (ticks, signals, etc.).
    self.eventQueue = queue.Queue()

    # Create CsvData class object.
    dataProvider = 'iVolatility'  # iVolatility_futures'
    filename = '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/combinedSPX_1990_2023.csv'
    self.dataHandler = csvData.CsvData(csvPath=filename, dataProvider=dataProvider, eventQueue=self.eventQueue)

    # Parameters for strategy.
    expCycle = strategy.ExpirationTypes.ANY
    startDateTime = '01/01/2005'
    startDateTimeFormatted = datetime.datetime.strptime(startDateTime, '%m/%d/%Y')
    # Save maxCapitalToUse in the session since the run function requires it.
    self.maxCapitalToUse = 0.5  # Up to 50% of net liq can be used in trades.
    maxCapitalToUsePerTrade = 0.10  # 10% max capital to use per trade / strategy.
    startingCapital = 1000000
    strategyName = 'PUT_VERTICAL_ON_DOWN_MOVE'
    riskManagement = 'CLOSE_AT_50_PERCENT'
    closeDuration = 10  # Number of days from expiration to close the trade.
    percentDownToTrigger = 0.1  # 10%
    numberDaysForMovingAverage = 10
    optPutToBuyDelta = -0.10
    maxPutToBuyDelta = -0.14
    minPutToBuyDelta = -0.06
    optPutToSellDelta = -0.16
    maxPutToSellDelta = -0.20
    minPutToSellDelta = -0.12
    underlyingTicker = 'SPX'
    orderQuantity = 1
    contractMultiplier = 100
    optimalDTE = 45
    minimumDTE  = 35
    maximumDTE = 55
    maxBidAsk = 15  # Set to a large value to effectively disable.

    # Set up portfolio and position monitoring.
    self.positionMonitoring = defaultdict(list)
    pricingSource = 'tastyworks'  # 'tastyworks_futures'
    pricingSourceConfigFile = '/Users/msantoro/PycharmProjects/Backtester/dataHandler/pricingConfig.json'
    self.portfolioManager = portfolio.Portfolio(decimal.Decimal(startingCapital), self.maxCapitalToUse,
                                                maxCapitalToUsePerTrade, positionMonitoring=self.positionMonitoring)

    if strategyName == 'PUT_VERTICAL_ON_DOWN_MOVE':
      # TODO(msantoro): If statements below should use polymorphism where the riskManagement.py has all of the base
      # risk management types.
      if riskManagement == 'HOLD_TO_EXPIRATION':
        riskManagement = putVerticalRiskManagement.PutVerticalManagementStrategyTypes.HOLD_TO_EXPIRATION
      elif riskManagement == 'CLOSE_AT_50_PERCENT':
        riskManagement = putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT
      elif riskManagement == 'CLOSE_AT_50_PERCENT_OR_21_DAYS':
        riskManagement = putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS
      elif riskManagement == 'CLOSE_AT_50_PERCENT_OR_21_DAYS_OR_HALFLOSS':
        riskManagement = putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS_OR_HALFLOSS
      elif riskManagement == 'CLOSE_AT_21_DAYS':
        riskManagement = putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_21_DAYS
      else:
        raise ValueError('Risk management type not supported.')
      if closeDuration <= 0:
        closeDuration = None
      riskManagementStrategy = putVerticalRiskManagement.PutVerticalRiskManagement(riskManagement, closeDuration)
      self.strategyManager = putVerticalOnDownMoveStrat.PutVerticalOnDownMoveStrat(
        self.eventQueue, percentDownToTrigger, numberDaysForMovingAverage,
        optPutToBuyDelta, maxPutToBuyDelta, minPutToBuyDelta,
        optPutToSellDelta, maxPutToSellDelta, minPutToSellDelta,
        underlyingTicker, orderQuantity, contractMultiplier,
        riskManagementStrategy, pricingSource, pricingSourceConfigFile, expCycle, optimalDTE,
        minimumDTE, maximumDTE, maxBidAsk=maxBidAsk,
        maxCapitalToUsePerTrade=maxCapitalToUsePerTrade, startDateTime=startDateTimeFormatted)

      # Write params to log file to be able to track experiments.
      # Set up logging for the session.
      logging.basicConfig(filename='log.log', level=logging.DEBUG)
      logging.info(
        'optPutToSellDelta: {}  maxPutToSellDelta: {} minPutToSellDelta: {} optPutToBuyDelta: {} maxPutToBuyDelta: {} minPutToBuyDelta: {} underlyingTicker: {} orderQuantity: {} expCycle: {} optimalDTE: {} minimumDTE: {} maximumDTE: {} maxBidAsk: {} percentDownToTrigger: {} numberDaysForMovingAverage: {} riskManagement: {} startingCapital: {} self.maxCapitalToUse: {} maxCapitalToUsePerTrade: {} pricingSource: {}'.format(
          currentStrategy.optPutToSellDelta, currentStrategy.maxPutToSellDelta,
          currentStrategy.minPutToSellDelta, currentStrategy.optPutToBuyDelta, currentStrategy.maxPutToBuyDelta,
          currentStrategy.minPutToBuyDelta, currentStrategy.underlyingTicker, currentStrategy.orderQuantity, expCycle,
          currentStrategy.optimalDTE, currentStrategy.minimumDTE, currentStrategy.maximumDTE, currentStrategy.maxBidAsk,
          currentStrategy.percentDownToTrigger, currentStrategy.numberDaysForMovingAverage,
          riskManagementStrategy.getRiskManagementType(), currentStrategy.startingCapital, self.maxCapitalToUse,
          currentStrategy.maxCapitalToUsePerTrade, pricingSource))
    elif strategyName == 'SHORT_NAKED_PUT':
      if riskManagement == 'HOLD_TO_EXPIRATION':
        riskManagement = shortNakedPutRiskManagement.ShortNakedPutManagementStrategyTypes.HOLD_TO_EXPIRATION
      elif riskManagement == 'CLOSE_AT_50_PERCENT':
        riskManagement = shortNakedPutRiskManagement.ShortNakedPutManagementStrategyTypes.CLOSE_AT_50_PERCENT
      elif riskManagement == 'CLOSE_AT_50_PERCENT_OR_21_DAYS':
        riskManagement = shortNakedPutRiskManagement.ShortNakedPutManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS
      elif riskManagement == 'CLOSE_AT_50_PERCENT_OR_21_DAYS_OR_HALFLOSS':
        riskManagement = shortNakedPutRiskManagement.ShortNakedPutManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS_OR_HALFLOSS
      elif riskManagement == 'CLOSE_AT_21_DAYS':
        riskManagement = shortNakedPutRiskManagement.ShortNakedPutManagementStrategyTypes.CLOSE_AT_21_DAYS
      else:
        raise ValueError('Risk management type not supported.')
      riskManagementStrategy = shortNakedPutRiskManagement.ShortNakedPutRiskManagement(riskManagement)
      self.strategyManager = nakedPutStrat.NakedPutStrat(self.eventQueue, currentStrategy.optPutToSellDelta,
                                                         currentStrategy.maxPutToSellDelta,
                                                         currentStrategy.minPutToSellDelta,
                                                         currentStrategy.underlyingTicker,
                                                         currentStrategy.orderQuantity,
                                                         currentStrategy.contractMultiplier,
                                                         riskManagementStrategy, pricingSource,
                                                         pricingSourceConfigFile,
                                                         expCycle, currentStrategy.optimalDTE,
                                                         currentStrategy.minimumDTE,
                                                         maxBidAsk=currentStrategy.maxBidAsk,
                                                         maxCapitalToUsePerTrade=currentStrategy.maxCapitalToUsePerTrade,
                                                         startDateTime=startDateTimeFormatted)

      # Write params to log file to be able to track experiments.
      # Set up logging for the session.
      logging.basicConfig(filename='log.log', level=logging.DEBUG)
      logging.info(
        'optPutToSellDelta: {}  maxPutToSellDelta: {} minPutToSellDelta: {} underlyingTicker: {} orderQuantity: {} expCycle: {} optimalDTE: {} minimumDTE: {} maximumDTE: {} maxBidAsk: {} riskManagement: {} startingCapital: {} self.maxCapitalToUse: {} maxCapitalToUsePerTrade: {} pricingSource: {}'.format(
          currentStrategy.optPutToSellDelta, currentStrategy.maxPutToSellDelta,
          currentStrategy.minPutToSellDelta, currentStrategy.underlyingTicker, currentStrategy.orderQuantity, expCycle,
          currentStrategy.optimalDTE, currentStrategy.minimumDTE, currentStrategy.maximumDTE, currentStrategy.maxBidAsk,
          riskManagementStrategy.getRiskManagementType(), currentStrategy.startingCapital, self.maxCapitalToUse,
          currentStrategy.maxCapitalToUsePerTrade, pricingSource))
    else:
      raise ValueError('Strategy not supported.')


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
  # Create a session and configure the session.
  session = BackTestSession()

  # Run the session.
  run(session)

  # Write position monitoring to CSV file.
  with open('monitoring.csv', 'w') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(session.positionMonitoring.keys())
    writer.writerows(zip(*session.positionMonitoring.values()))