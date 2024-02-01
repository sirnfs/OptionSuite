import csv
import datetime
import decimal
import hydra
import logging
import queue
from dataHandler import csvData
from events import event as event_class
from omegaconf import DictConfig, OmegaConf
from riskManager import putVerticalRiskManagement, strangleRiskManagement, shortNakedPutRiskManagement
from strategyManager import strategy, StrangleStrat, putVerticalOnDownMoveStrat, nakedPutStrat
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
  def __init__(self, configStrategy: DictConfig):

    # Create queue to hold events (ticks, signals, etc.).
    self.eventQueue = queue.Queue()

    # Create CsvData class object.
    # TODO(msantoro): This should be moved to config for when we handle other data sources / types.
    dataProvider = 'iVolatility'  # iVolatility_futures'
    #filename = '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/ES/combinedES.csv'
    filename = '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/combinedSPX_1990_2023.csv'
    #filename = '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/combinedCSV.csv'
    self.dataHandler = csvData.CsvData(csvPath=filename, dataProvider=dataProvider, eventQueue=self.eventQueue)

    # Parameters for strategy.
    currentStrategy = configStrategy.strategy
    expCycle = strategy.ExpirationTypes.ANY
    #if currentStrategy.expCycle == 'MONTHLY':
    # expCycle = strategy.ExpirationTypes.MONTHLY
    #else:
    #  raise ValueError('Expiration cycles other than monthly not supported.')
    startDateTimeFormatted = datetime.datetime.strptime(currentStrategy.startDateTime, '%m/%d/%Y')
    # Save maxCapitalToUse in the session since the run function requires it.
    self.maxCapitalToUse = currentStrategy.maxCapitalToUse

    # Set up portfolio and position monitoring.
    self.positionMonitoring = defaultdict(list)
    pricingSource = 'tastyworks'  # 'tastyworks_futures'
    pricingSourceConfigFile = '/Users/msantoro/PycharmProjects/Backtester/dataHandler/pricingConfig.json'
    self.portfolioManager = portfolio.Portfolio(decimal.Decimal(currentStrategy.startingCapital),
                                                self.maxCapitalToUse,
                                                currentStrategy.maxCapitalToUsePerTrade,
                                                positionMonitoring=self.positionMonitoring)

    if currentStrategy.strategyName == 'PUT_VERTICAL_ON_DOWN_MOVE':
      # TODO(msantoro): If statements below should use polymorphism where the riskManagement.py has all of the base
      # risk management types.
      if currentStrategy.riskManagement == 'HOLD_TO_EXPIRATION':
        riskManagement = putVerticalRiskManagement.PutVerticalManagementStrategyTypes.HOLD_TO_EXPIRATION
      elif currentStrategy.riskManagement == 'CLOSE_AT_50_PERCENT':
        riskManagement = putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT
      elif currentStrategy.riskManagement == 'CLOSE_AT_50_PERCENT_OR_21_DAYS':
        riskManagement = putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS
      elif currentStrategy.riskManagement == 'CLOSE_AT_50_PERCENT_OR_21_DAYS_OR_HALFLOSS':
        riskManagement = putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS_OR_HALFLOSS
      elif currentStrategy.riskManagement == 'CLOSE_AT_21_DAYS':
        riskManagement = putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_21_DAYS
      else:
        raise ValueError('Risk management type not supported.')
      if currentStrategy.closeDuration == 0:
        closeDuration = None
      else:
        closeDuration = currentStrategy.closeDuration
      riskManagementStrategy = putVerticalRiskManagement.PutVerticalRiskManagement(riskManagement, closeDuration)
      self.strategyManager = putVerticalOnDownMoveStrat.PutVerticalOnDownMoveStrat(
        self.eventQueue, currentStrategy.percentDownToTrigger, currentStrategy.numberDaysForMovingAverage,
        currentStrategy.optPutToBuyDelta, currentStrategy.maxPutToBuyDelta, currentStrategy.minPutToBuyDelta,
        currentStrategy.optPutToSellDelta, currentStrategy.maxPutToSellDelta, currentStrategy.minPutToSellDelta,
        currentStrategy.underlyingTicker, currentStrategy.orderQuantity, currentStrategy.contractMultiplier,
        riskManagementStrategy, pricingSource, pricingSourceConfigFile, expCycle, currentStrategy.optimalDTE,
        currentStrategy.minimumDTE, currentStrategy.maximumDTE, maxBidAsk=currentStrategy.maxBidAsk,
        maxCapitalToUsePerTrade=currentStrategy.maxCapitalToUsePerTrade, startDateTime=startDateTimeFormatted)

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
    elif currentStrategy.strategyName == 'SHORT_NAKED_PUT':
      if currentStrategy.riskManagement == 'HOLD_TO_EXPIRATION':
        riskManagement = shortNakedPutRiskManagement.ShortNakedPutManagementStrategyTypes.HOLD_TO_EXPIRATION
      elif currentStrategy.riskManagement == 'CLOSE_AT_50_PERCENT':
        riskManagement = shortNakedPutRiskManagement.ShortNakedPutManagementStrategyTypes.CLOSE_AT_50_PERCENT
      elif currentStrategy.riskManagement == 'CLOSE_AT_50_PERCENT_OR_21_DAYS':
        riskManagement = shortNakedPutRiskManagement.ShortNakedPutManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS
      elif currentStrategy.riskManagement == 'CLOSE_AT_50_PERCENT_OR_21_DAYS_OR_HALFLOSS':
        riskManagement = shortNakedPutRiskManagement.ShortNakedPutManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS_OR_HALFLOSS
      elif currentStrategy.riskManagement == 'CLOSE_AT_21_DAYS':
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


@hydra.main(config_path="sweepConfig", config_name="config", version_base=None)
def setUpHydra(cfg : DictConfig) -> None:
  print(OmegaConf.to_yaml(cfg))

  # Create a session and configure the session.
  session = BackTestSession(cfg)

  # Run the session.
  run(session)

  # Write position monitoring to CSV file.
  with open('monitoring.csv', 'w') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(session.positionMonitoring.keys())
    writer.writerows(zip(*session.positionMonitoring.values()))

if __name__ == "__main__":
  setUpHydra()


 # # Parameters for strangle strategy -- TODO: move params to hydra.
    # optCallDelta = 0.16
    # maxCallDelta = 0.30
    # optPutDelta = -0.16
    # maxPutDelta = -0.30
    # startDateTime = None
    # buyOrSell = optionPrimitive.TransactionType.SELL
    # underlyingTicker = 'SPX'
    # orderQuantity = 1
    # expCycle = strategy.ExpirationTypes.MONTHLY
    # optimalDTE = 45
    # minimumDTE = 35
    # maxBidAsk = 15 # A general rule of thumb is to take 0.001*underlyingPrice.  Set to 15 to ignore field.
    # startingCapital = decimal.Decimal(200000)
    # self.maxCapitalToUse = 0.5  # Up to 50% of net liq can be used in trades.
    # maxCapitalToUsePerTrade = 0.10  # 10% max capital to use per trade / strategy.
    # # Set up strategy (strangle strategy) and risk management preference.
    # riskManagement = strangleRiskManagement.StrangleRiskManagement(
    #   strangleRiskManagement.StrangleManagementStrategyTypes.CLOSE_AT_50_PERCENT)  # strangleRiskManagement.StrangleManagementStrategyTypes.HOLD_TO_EXPIRATION)
    # self.strategyManager = strangleStrat.StrangleStrat(self.eventQueue, optCallDelta, maxCallDelta, optPutDelta,
    #                                                    maxPutDelta, buyOrSell, underlyingTicker,
    #                                                    orderQuantity, riskManagement, expCycle, optimalDTE,
    #                                                    minimumDTE, maxBidAsk=maxBidAsk,
    #                                                    maxCapitalToUsePerTrade=maxCapitalToUsePerTrade,
    #                                                    startDateTime=startDateTime)
    #
    # # Set up portfolio.
    # # Dictionary used to keep track of portfolio value changes.
    # self.positionMonitoring = defaultdict(list)
    # pricingSource = 'tastyworks'
    # pricingSourceConfigFile = './dataHandler/pricingConfig.json'
    # self.portfolioManager = portfolio.Portfolio(startingCapital, self.maxCapitalToUse, maxCapitalToUsePerTrade,
    #                                             positionMonitoring=self.positionMonitoring,
    #                                             pricingSource=pricingSource,
    #                                             pricingSourceConfigFile=pricingSourceConfigFile)
    # # Write params to log file to be able to track experiments.
    # logging.info(
    #   'optCallDelta: {} maxCallDelta: {} optPutDelta: {} maxPutDelta: {} startDateTime: {} underlyingTicker: {} orderQuantity: {} expCycle: {} optimalDTE: {} minimumDTE: {} maxBidAsk: {} riskManagement: {} startingCapital: {} self.maxCapitalToUse: {} maxCapitalToUsePerTrade: {} pricingSource: {}'.format(
    #     optCallDelta, maxCallDelta, optPutDelta, maxPutDelta, startDateTime, underlyingTicker, orderQuantity, expCycle,
    #     optimalDTE, minimumDTE, maxBidAsk, riskManagement.getRiskManagementType(), startingCapital,
    #     self.maxCapitalToUse, maxCapitalToUsePerTrade, pricingSource))