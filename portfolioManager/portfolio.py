import logging

class Portfolio(object):
    """This class creates a portfolio to hold all open positions
       At the moment, the portfolio runs live, but in the future we should migrate the portfolio to be stored in a
       database.

       Portfolio inputs:
       startingCapital -- how much capital we have when starting
       maxCapitalToUse -- max percent of portfolio to use (decimal between 0 and 1)
       maxCapitalToUsePerTrade -- max percent of portfolio to use on one trade (same underlying), 0 to 1

       Portfolio intrinsics:
       realizedCapital:  updated when positions are actually closed
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
        self.__realizedCapital = startingCapital
        self.__netLiq = startingCapital
        self.__totBuyingPower = 0
        self.__PLopen = 0
        self.__PLday = 0
        self.__PLopenPercent = 0
        self.__PLdayPercent = 0
        self.__totDelta = 0
        self.__totVega = 0
        self.__totTheta = 0
        self.__totGamma = 0

        # Array / list to hold option primitives
        self.__positions = []

    def getNetLiq(self):
        return self.__netLiq

    def getStartingCapital(self):
        return self.__startingCapital

    def getTotalBuyingPower(self):
        return self.__totBuyingPower

    def getDelta(self):
        return self.__totDelta

    def getTheta(self):
        return self.__totTheta

    def getVega(self):
        return self.__totVega

    def getGamma(self):
        return self.__totGamma

    def getPositions(self):
        return self.__positions

    def onSignal(self, event):
        """Handle a new signal event; indicates that a new position should be added to the portfolio
        if portfolio risk management conditions are satisfied

        :param event: event to be handled by portfolio; signal event in this case

        """
        # Get the data from the tick event
        eventData = event.getData()

        # Return if there's no data
        if not eventData:
            return

        # Determine if the eventData meets the portfolio risk management -- this will eventually be moved to
        # a separate risk management module
        tradeCapReq = eventData.getBuyingPower()

        # Check if we already have this underlying in the portfolio; if so, return.
        # TODO: need a better way to do this; enable / disable from the portfolio initialization
        if self.__underlyingExists(eventData):
            return

        # If we have not used too much total buying power in the portfolio, and the current trade is using less
        # than the maximum allowed per trade, we add the position to the portfolio
        if ((self.__totBuyingPower < self.__netLiq*self.__maxCapitalToUse) and
            (tradeCapReq < self.__netLiq*self.__maxCapitalToUsePerTrade)):
            self.__positions.append(eventData)
            self.__totBuyingPower += eventData.getBuyingPower()

            # Update total delta, vega, theta and gamma for portfolio
            if eventData.getDelta():
                self.__totDelta += eventData.getDelta()
            else:
                logging.warning("No delta values were found in the option primitive")
            if eventData.getGamma():
                self.__totGamma += eventData.getGamma()
            else:
                logging.warning("No gamma values were found in the option primitive")
            if eventData.getTheta():
                self.__totTheta += eventData.getTheta()
            else:
                logging.warning("No theta values were found in the option primitive")
            if eventData.getVega():
                self.__totVega += eventData.getVega()
            else:
                logging.warning("No vega values were found in the option primitive")
        else:
            if self.__totBuyingPower >= self.__netLiq * self.__maxCapitalToUse:
                logging.info("Not enough buying power available based on maxCapitalToUse threshold")
            else:
                logging.info("Trade uses too much buying power based on maxCapitalToUsePerTrade threshold")

    def updatePortfolio(self, event):
        """
        Updates the intrinsics of the portfolio by updating the values of the options used in the different
        optionPrimitives.
        :param event: tick event with the option chain which will be be used to update the portfolio
        """

        # Get the data from the tick event
        tickData = event.getData()

        # If we did not get any tick data or there are not positions in the portfolio, return
        if not tickData or not self.__positions:
            return

        # Go through the positions currently in the portfolio and update the prices
        # Reset the delta, gamma, theta, and vega values for the entire portfolio
        self.__totDelta = 0
        self.__totGamma = 0
        self.__totVega = 0
        self.__totTheta = 0
        # Reset the total buying power for the portfolio, which will be recalculated
        self.__totBuyingPower = 0
        # Reset the netLiq
        self.__netLiq = 0
        # Reset the PLopen, PLday, PLopenPercent PLdayPercent
        self.__PLopen = 0
        self.__PLday = 0
        self.__PLopenPercent = 0
        self.__PLdayPercent = 0

        # Array / list used to keep track of which positions we should remove after calling __managePosition
        idxsToDelete = []

        # Go through all positions in portfolio and do the updates
        for idx, curPosition in enumerate(self.__positions):
            # Update the option intrinsic values
            curPosition.updateValues(tickData)

            # Determine if we should close out this position or do some type of management
            positionClosed = self.__managePosition(curPosition)

            # Update portfolio values; e.g., total delta, vega, buying power, net liq
            if not positionClosed:
                self.__calcPortfolioValues(curPosition)
                self.__netLiq += curPosition.calcProfitLoss()
            else:
                idxsToDelete.append(idx)

        # Add the realized capital to the profit / loss of all open positions to get final net liq
        self.__netLiq += self.__realizedCapital
        #print("Net liq: ${}").format(self.__netLiq)
        logging.info("Net liq: %f", self.__netLiq)

        # Go through and delete any positions which were added to the idxsToDelete array
        for idx in idxsToDelete:
            #print("The {} position was closed").format(self.__positions[idx].getUnderlyingTicker())
            logging.info('The %s position was closed', self.__positions[idx].getUnderlyingTicker())
            del(self.__positions[idx])

    def __underlyingExists(self, position):
        """Check if the underlying we're trying to add to the portfolio already exists
        :param: position:  position we're trying to add to the portfolio
        :return: True if there the underlying is already in the portfolio; False otherwise.
        """
        for curPosition in self.__positions:
            if curPosition.getUnderlyingTicker() == position.getUnderlyingTicker():
                logging.warning('Tried to add a position to the portfolio that already exists')
                return True

        return False

    def __calcPortfolioValues(self, curPosition):
        """Private /internal function used to update portfolio values

        :param curPosition: current position in portfolio being processed
        """

        if curPosition.getDelta():
            self.__totDelta += curPosition.getDelta()
        else:
            logging.warning("No delta values were found in the option primitive after tick update")
        if curPosition.getGamma():
            self.__totGamma += curPosition.getGamma()
        else:
            logging.warning("No gamma values were found in the option primitive after tick update")
        if curPosition.getTheta():
            self.__totTheta += curPosition.getTheta()
        else:
            logging.warning("No theta values were found in the option primitive after tick update")
        if curPosition.getVega():
            self.__totVega += curPosition.getVega()
        else:
            logging.warning("No vega values were found in the option primitive after tick update")

        # Update the buying power
        self.__totBuyingPower += curPosition.getBuyingPower()

        # TODO:  handle PLopen, PLday, PLopenPercent PLdayPercent calculations

    def __managePosition(self, curPosition):
        """Private / internal function to determine if we need to manage position (e.g., close out position or make
        adjustments)
        :param curPosition:  current position we are looking at in portfolio
        :return: True if position was closed; False otherwise
        """

        # Determine if the position should be managed by calling respective option primitive managePosition() function
        if curPosition.managePosition():

            # Update realized capital
            self.__realizedCapital += curPosition.calcProfitLoss()

            # Returning true indicates that position will be deleted
            return True

        return False