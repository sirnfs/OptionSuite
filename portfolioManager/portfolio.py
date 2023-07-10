import dataclasses
import decimal
import json
import logging
import typing
from events import signalEvent, tickEvent
from optionPrimitives import optionPrimitive

@dataclasses.dataclass()
class Portfolio(object):
  """This class creates a portfolio to hold all open positions.
  At the moment, the portfolio runs live, but in the future we should migrate the portfolio to be stored in a
  database.

  Attributes:
    startingCapital -- How much capital we have when starting.
    maxCapitalToUse -- Max percent of portfolio to use (decimal between 0 and 1).
    maxCapitalToUsePerTrade -- Max percent of portfolio to use on one trade (same underlying), 0 to 1.
    positionMonitoring -- Used to keep track of portfolio values over time.
    pricingSource -- Used to indicate which brokerage to use for commissions / fees.
    pricingSourceConfig -- File path to the JSON config file for commission / fees.

  Portfolio intrinsics:
    realizedCapital:  Updated when positions are actually closed.
    netLiquidity:  Net liquidity of total portfolio (ideally includes commissions, fees, etc.).
    totalBuyingPower:  Total buying power being used in portfolio.
    openProfitLoss:  Current value of open positions in dollars (positive or negative).
    dayProfitLoss:  Amount of money gained / lost for the current day in dollars (positive or negative).
    openProfitLossPercent:  Same as PLopen, but expressed as a percent of total capital being used.
    dayProfitLossPercent:  Same as PLday, but expressed as a percentage of total capital being used.
    totalDelta:  Sum of deltas for all positions (positive or negative).
    totalVega:  Sum of vegas for all positions (positive or negative).
    totalTheta:  Sum of thetas for all positions (positive or negative).
    totalGamma:  Sum of gammas for all positions (positive or negative).
  """

  startingCapital: decimal.Decimal
  maxCapitalToUse: float
  maxCapitalToUsePerTrade: float
  positionMonitoring: typing.Optional[typing.DefaultDict[typing.Text, list]] = None
  pricingSource: typing.Optional[typing.Text] = None
  pricingSourceConfigFile: typing.Optional[typing.Text] = None
  realizedCapital: typing.ClassVar[decimal.Decimal]
  netLiquidity: typing.ClassVar[decimal.Decimal]
  totalBuyingPower: typing.ClassVar[decimal.Decimal] = decimal.Decimal(0.0)
  openProfitLoss: typing.ClassVar[decimal.Decimal] = decimal.Decimal(0.0)
  dayProfitLoss: typing.ClassVar[decimal.Decimal] = decimal.Decimal(0.0)
  openProfitLossPercent: typing.ClassVar[float] = 0.0
  dayProfitLossPercent: typing.ClassVar[float] = 0.0
  totalDelta: typing.ClassVar[float] = 0.0
  totalVega: typing.ClassVar[float] = 0.0
  totalTheta: typing.ClassVar[float] = 0.0
  totalGamma: typing.ClassVar[float] = 0.0
  totalNumberContracts: typing.ClassVar[int] = 0
  activePositions: typing.ClassVar[list] = []

  def __post_init__(self):
    self.realizedCapital = self.startingCapital
    self.netLiquidity = self.startingCapital
    self.activePositions = []

    # Open JSON file and select the pricingSource.
    self.pricingSourceConfig = None
    if self.pricingSource is not None and self.pricingSourceConfigFile is not None:
      with open(self.pricingSourceConfigFile) as config:
        fullConfig = json.load(config)
        self.pricingSourceConfig = fullConfig[self.pricingSource]

  def onSignal(self, event: signalEvent) -> None:
    """Handle a new signal event; indicates that a new position should be added to the portfolio if portfolio risk
    management conditions are satisfied.

    :param event: Event to be handled by portfolio; a signal event in this case.
    """
    # Get the data from the tick event
    eventData = event.getData()

    # Return if there's no data
    if not eventData:
      return

    positionData = eventData[0]

    # Determine if the eventData meets the portfolio criteria for adding a position.
    tradeCapitalRequirement = positionData.getBuyingPower()

    # Determine the commissions that the trade requires.
    openCommissionFeeCapitalRequirement = positionData.getCommissionsAndFees('open', self.pricingSourceConfig)

    # Amount of buying power that would be used with this strategy.
    currentTradeBuyingPower = tradeCapitalRequirement + openCommissionFeeCapitalRequirement
    tentativeBuyingPower = self.totalBuyingPower + currentTradeBuyingPower

    # If we have not used too much total buying power in the portfolio, and the current trade is using less
    # than the maximum allowed per trade, we add the position to the portfolio.
    if ((tentativeBuyingPower < self.netLiquidity*decimal.Decimal(self.maxCapitalToUse)) and
        (tradeCapitalRequirement < self.netLiquidity*decimal.Decimal(self.maxCapitalToUsePerTrade))):
      self.activePositions.append(eventData)
      self.totalBuyingPower += currentTradeBuyingPower
      # Reduce the realized capital by the commissions and fees.
      self.realizedCapital -= openCommissionFeeCapitalRequirement

      # Update delta, vega, theta and gamma for portfolio.
      self.totalDelta += positionData.getDelta()
      self.totalGamma += positionData.getGamma()
      self.totalTheta += positionData.getTheta()
      self.totalVega += positionData.getVega()
    else:
      if tentativeBuyingPower >= self.netLiquidity * decimal.Decimal(self.maxCapitalToUse):
        logging.info("Not enough buying power available based on maxCapitalToUse threshold.")
      else:
        logging.info("Trade uses too much buying power based on maxCapitalToUsePerTrade threshold.")

  def updatePortfolio(self, event: tickEvent) -> None:
    """ Updates the intrinsics of the portfolio by updating the values of the options used in the different
    optionPrimitives.
    :param event: Tick event with the option chain which will be be used to update the portfolio.
    """
    # Get the data from the tick event.
    tickData = event.getData()

    # If we did not get any tick data or there are no positions in the portfolio, return.
    if not tickData or not self.activePositions:
      return

    # Go through the positions currently in the portfolio and update the prices.
    # We first reset the entire portfolio and recalculate the values.
    self.totalDelta = 0
    self.totalGamma = 0
    self.totalVega = 0
    self.totalTheta = 0
    self.totalBuyingPower = 0
    self.netLiquidity = 0
    self.openProfitLoss = 0
    self.dayProfitLoss = 0
    self.openProfitLossPercent = 0
    self.dayProfitLossPercent = 0
    self.totalNumberContracts = 0

    # Array / list used to keep track of which positions we should remove.
    idxsToDelete = []

    # Go through all positions in portfolio and update the values.
    currentDateTime = None
    for idx, curPosition in enumerate(self.activePositions):
      positionData = curPosition[0]
      riskMangementStrategy = curPosition[1]

      # Update the position values and check if we need to manage the position.
      if not positionData.updateValues(tickData) or riskMangementStrategy.managePosition(positionData):
        # If we can't update the values, we have to remove the position. Sometimes this happens when we have
        # incomplete option data. Otherwise, we see if we need to manage the position.
        self.realizedCapital += positionData.calcProfitLoss() - positionData.getCommissionsAndFees(
          'close', self.pricingSourceConfig)
        idxsToDelete.append(idx)
      else:
        self.netLiquidity += positionData.calcProfitLoss()
        # Update greeks and total buying power.
        self.__calcPortfolioValues(positionData)
        self.totalNumberContracts += positionData.getNumContracts()

      currentDateTime = positionData.getDateTime()
      underlyingPrice = positionData.getUnderlyingPrice()

    # Add the realized capital to the profit / loss of all open positions to get final net liq.
    self.netLiquidity += self.realizedCapital

    # Go through and delete any positions which were added to the idxsToDelete array.
    for idx in reversed(idxsToDelete):
      logging.info('The %s position was closed.', self.activePositions[idx][0].getUnderlyingTicker())
      del(self.activePositions[idx])

    if self.positionMonitoring is not None:
      # Update the position monitoring dictionary.
      self.positionMonitoring['Date'].append(currentDateTime)
      self.positionMonitoring['UnderlyingPrice'].append(underlyingPrice)
      self.positionMonitoring['NetLiq'].append(self.netLiquidity)
      self.positionMonitoring['RealizedCapital'].append(self.realizedCapital)
      self.positionMonitoring['NumPositions'].append(len(self.activePositions))
      self.positionMonitoring['TotNumContracts'].append(self.totalNumberContracts)
      self.positionMonitoring['BuyingPower'].append(self.totalBuyingPower)
      self.positionMonitoring['TotalDelta'].append(self.totalDelta)

    logging.info(
      'Date: {} UnderlyingPrice: {} NetLiq: {} RealizedCapital: {} NumPositions: {} TotNumContracts: {} BuyingPower: {} TotalDelta: {}'.format(
        currentDateTime, underlyingPrice, self.netLiquidity, self.realizedCapital, len(self.activePositions),
        self.totalNumberContracts, self.totalBuyingPower, self.totalDelta))

  def __calcPortfolioValues(self, curPosition: optionPrimitive.OptionPrimitive) -> None:
    """Updates portfolio values for current position.

    :param curPosition: Current position in portfolio being processed.
    """
    self.totalDelta += curPosition.getDelta()
    self.totalGamma += curPosition.getGamma()
    self.totalTheta += curPosition.getTheta()
    self.totalVega += curPosition.getVega()
    self.totalBuyingPower += curPosition.getBuyingPower()

    # TODO: Add self.openProfitLoss,self.dayProfitLoss,self.openProfitLossPercent, and self.dayProfitLossPercent.