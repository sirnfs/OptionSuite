
class Portfolio(object):
    """This class creates a portfolio to hold all open positions
       At the moment, the portfolio runs live, but in the future we should migrate the portfolio to be stored in a
       database.

       Portfolio inputs:
       startingCapital -- how much capital we have when starting
       maxCapitalToUse -- max percent of portfolio to use (integer between 0 to 100)
       maxCapitalToUsePerTrade -- max percent of portfolio to use on one trade (same underlying), 0 to 100

       Portfolio intrinsics:
       netLiq:  net liquidity of total portfolio (ideally includes commissions, fees, etc.)
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

        # Portfolio risk management
        self.__startingCapital = startingCapital
        self.__maxCapitalToUse = maxCapitalToUse
        self.__maxCapitalToUsePerTrade = maxCapitalToUsePerTrade

        # Overall portfolio intrinsics
        self.__netLiq = None
        self.__PLopen = None
        self.__PLday = None
        self.__PLopenPercent = None
        self.__PLdayPercent = None
        self.__totDelta = None
        self.__totVega = None
        self.__totTheta = None
        self.__totGamma = None

        # Array to hold option primitives
        self.positions = None

    def onSignal(self, event):
        """Handle a new signal event; indicates that a new position should be added to the portfolio
        if portfolio risk conditions are satisfied

        :param event: event to be handled by portfolio; signal event in this case

        """

        pass







