
class Portfolio(object):
    """This class creates a portfolio to hold all open positions
       At the moment, the portfolio runs live, but in the future we should migrate the portfolio to be stored in a
       database.

       Portfolio inputs:
       startingCapital -- how much capital we have when starting
       maxCapitalToUse -- max percent of portfolio to use (decimal between 0 and 1)
       maxCapitalToUsePerTrade -- max percent of portfolio to use on one trade (same underlying), 0 to 1

       Portfolio intrinsics:
       netLiq:  net liquidity of total portfolio (ideally includes commissions, fees, etc.)
       totBuyingPower:  total buying power being used in portfolio
       PLopen:  current value of open positions in dollars (positive or negative)
       PLday:  amount of money gained / lost for the current day in dollars (positive or negative)
       PLopenPercent:  same as PLopen, but expressed as a percent of total capital being used
       PLdayPecent:  same as PLday, but expressed as a percentage of total capital being used
       totDelta:  sum of deltas for all positions (positive or negative)
       totVega:  sum of vegas for all positions (positive or negative)
       totTheta:  sum of thetas for all positions (positive or negative)
       totGamma:  sum of gammas for all positions (positive or negative)

    """

    def __init__(self, startingCapital, maxCapitalToUse, maxCapitalToUsePerTrade):

        self.__startingCapital = startingCapital

        # Portfolio risk management
        self.__maxCapitalToUse = maxCapitalToUse
        self.__maxCapitalToUsePerTrade = maxCapitalToUsePerTrade

        # Overall portfolio intrinsics
        self.__netLiq = startingCapital
        self.__totBuyingPower = 0
        self.__PLopen = None
        self.__PLday = None
        self.__PLopenPercent = None
        self.__PLdayPercent = None
        self.__totDelta = None
        self.__totVega = None
        self.__totTheta = None
        self.__totGamma = None

        # Array / list to hold option primitives
        self.__positions = []

    def getNetLiq(self):
        return self.__netLiq

    def getStartingCapital(self):
        return self.__startingCapital

    def getTotalBuyingPower(self):
        return self.__totBuyingPower

    def getPositions(self):
        return self.__positions

    def onSignal(self, event):
        """Handle a new signal event; indicates that a new position should be added to the portfolio
        if portfolio risk management conditions are satisfied

        :param event: event to be handled by portfolio; signal event in this case

        """
        # Get the data from the tick event
        eventData = event.getData()

        # Determine if the eventData meets the portfolio risk management -- this will eventually be moved to
        # a separate risk management module
        tradeCapReq = eventData.getBuyingPower()

        # If we have not used too much total buying power in the portfolio, and the current trade is using less
        # than the maximum allowed per trade, we add the position to the portfolio
        if ((self.__totBuyingPower < self.__netLiq*self.__maxCapitalToUse) and
            (tradeCapReq < self.__netLiq*self.__maxCapitalToUsePerTrade)):
            self.__positions.append(eventData)
            self.__totBuyingPower += eventData.getBuyingPower()

            # TODO: update delta, vega, theta, gamma







