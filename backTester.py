import csv
import datetime
import decimal
import logging
import queue
from dataHandler import csvData
from events import event as event_class
from riskManager import putVerticalRiskManagement
from strategyManager import strategy, putVerticalStrat
from portfolioManager import portfolio
from collections import defaultdict

"""
This file runs the end-to-end backtesting session.
"""


class BackTestSession(object):
  """Class for holding all parameters of backtesting session."""

  def __init__(self):

    # Create queue to hold events (ticks, signals, etc.).
    self.eventQueue = queue.Queue()

    # Create CsvData class object.
    dataProviderPath = '/Users/msantoro/PycharmProjects/Backtester/dataHandler/dataProviders.json'
    dataProvider = 'iVolatility'  # iVolatility_futures'
    # TODO(msantoro): does this CSV below have settlement price correctly?
    filename = '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/combinedCSV.csv' #combinedSPX_1990_2023.csv'
    self.dataHandler = csvData.CsvData(csvPath=filename, dataProviderPath=dataProviderPath, dataProvider=dataProvider,
                                       eventQueue=self.eventQueue)

    # Parameters for strategy.
    startDateTime = '01/01/1990'
    startDateTimeFormatted = datetime.datetime.strptime(startDateTime, '%m/%d/%Y')
    # Save maxCapitalToUse in the session since the run function requires it.
    self.maxCapitalToUse = decimal.Decimal(0.45)  # Up to 45% of net liq can be used in trades.
    maxCapitalToUsePerTrade = decimal.Decimal(0.30)  # 30% max capital to use per trade / strategy.
    startingCapital = 1000000
    strategyName = 'PUT_VERTICAL_STRAT'
    riskManagement = 'CLOSE_AT_50_PERCENT_OR_21_DAYS'
    closeDuration = 0 # Number of days from expiration to close the trade.
    optPutToBuyDelta = -0.09
    maxPutToBuyDelta = -0.1
    minPutToBuyDelta = -0.005
    optPutToSellDelta = -0.175
    maxPutToSellDelta = -0.25
    minPutToSellDelta = -0.11
    underlyingTicker = 'SPX'
    orderQuantity = 1
    contractMultiplier = 100
    optimalDTE = 45
    minimumDTE = 40
    maximumDTE = 55
    maxBidAsk = decimal.Decimal(15)  # Set to a large value to effectively disable.

    # Set up portfolio and position monitoring.
    self.positionMonitoring = defaultdict(list)
    pricingSource = 'tastyworks'  # 'tastyworks_futures'
    pricingSourceConfigFile = '/Users/msantoro/PycharmProjects/Backtester/dataHandler/pricingConfig.json'
    self.portfolioManager = portfolio.Portfolio(decimal.Decimal(startingCapital), self.maxCapitalToUse,
                                                maxCapitalToUsePerTrade, positionMonitoring=self.positionMonitoring)

    if strategyName == 'PUT_VERTICAL_STRAT':
      # TODO(msantoro): If statements below should use polymorphism where the riskManagement.py has all of the base
      # risk management types.
      if riskManagement == 'HOLD_TO_EXPIRATION':
        riskManagement = putVerticalRiskManagement.PutVerticalManagementStrategyTypes.HOLD_TO_EXPIRATION
      elif riskManagement == 'CLOSE_AT_50_PERCENT':
        riskManagement = putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT
      elif riskManagement == 'CLOSE_AT_50_PERCENT_OR_21_DAYS':
        riskManagement = putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS
      elif riskManagement == 'CLOSE_AT_50_PERCENT_OR_21_DAYS_OR_HALFLOSS':
        riskManagement = (
          putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS_OR_HALFLOSS)
      elif riskManagement == 'CLOSE_AT_21_DAYS':
        riskManagement = putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_21_DAYS
      else:
        raise ValueError('Risk management type not supported.')
      if closeDuration <= 0:
        closeDuration = None
      riskManagementStrategy = putVerticalRiskManagement.PutVerticalRiskManagement(riskManagement, closeDuration)
      self.strategyManager = putVerticalStrat.PutVerticalStrat(
        self.eventQueue, optPutToBuyDelta, maxPutToBuyDelta, minPutToBuyDelta, optPutToSellDelta, maxPutToSellDelta,
        minPutToSellDelta, underlyingTicker, orderQuantity, contractMultiplier, riskManagementStrategy, pricingSource,
        pricingSourceConfigFile, optimalDTE, minimumDTE, maximumDTE, maxBidAsk=maxBidAsk,
        maxCapitalToUsePerTrade=maxCapitalToUsePerTrade, startDateTime=startDateTimeFormatted)

      # Write params to log file to be able to track experiments.
      # Set up logging for the session.
      logging.basicConfig(filename='log.log', level=logging.DEBUG)
      logging.info(
        'optPutToSellDelta: {} maxPutToSellDelta: {} minPutToSellDelta: {} optPutToBuyDelta: {} maxPutToBuyDelta: {}'
        ' minPutToBuyDelta: {} underlyingTicker: {} orderQuantity: {} optimalDTE: {} minimumDTE: {}'
        ' maximumDTE: {} maxBidAsk: {} riskManagement: {}  startingCapital: {} self.maxCapitalToUse: {}'
        ' maxCapitalToUsePerTrade: {} pricingSource: {}'.format(
          optPutToSellDelta, maxPutToSellDelta, minPutToSellDelta, optPutToBuyDelta, maxPutToBuyDelta,
          minPutToBuyDelta, underlyingTicker, orderQuantity, optimalDTE, minimumDTE, maximumDTE, maxBidAsk,
          riskManagementStrategy.getRiskManagementType(), startingCapital, self.maxCapitalToUse,
          maxCapitalToUsePerTrade, pricingSource))
    else:
      raise ValueError('Strategy not supported.')


def run(session):
  while (1):  # Infinite loop to keep processing items in queue.
    try:
      event = session.eventQueue.get(False)
    except queue.Empty:
      # Get data for tick event.
      if not session.dataHandler.getNextTick():
        # Get out of infinite while loop; no more data available.
        break
    else:
      if event is not None:
        if event.type == event_class.EventTypes.TICK:
          session.portfolioManager.updatePortfolio(event)
          # We pass the net liquidity and available buying power to the strategy.
          availableBuyingPower = decimal.Decimal(
            session.maxCapitalToUse) * session.portfolioManager.netLiquidity - session.portfolioManager.totalBuyingPower
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
