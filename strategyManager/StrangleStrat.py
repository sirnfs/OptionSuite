import strategy
from events import signalEvent
from optionPrimitives import strangle

class StrangleStrat(strategy.Strategy):
    """This class sets up the basics for a SPECIFIC strategy that will be used;
       In this case, we set up the strangle strategy, which involves buying or
       selling strangles with certain parameters
       
       Strangle specific attributes:
           optCallDelta:  optimal delta for call, usually around 16 delta
           maxCallDelta:  max delta for call, usually around 30 delta
           optPutDelta:  optimal delta for put, usually around 16 delta
           maxPutDelta:  max delta for put, usually around 30 delta

       General strategy attributes:
            startDateTime:  date/time to start the live trading or backtest
            strategy:  option strategy to use -- e.g., iron condor, strangle
            buyOrSell:  do we buy an iron condor or sell an iron condor? "BUY" or "SELL"
            underlying:  which underlying to use for the strategy
            orderQuantity:  number of strangles, iron condors, etc
            daysBeforeClose:  number of days before expiration to close the trade

            optional attributes:

            expCycle:  specifies if we want to do monthly ('m'); unspecified means we can do weekly, quarterly, etc
            optimalDTE:  optimal number of days before expiration to put on strategy
            minimumDTE:  minimum number of days before expiration to put on strategy
            roc:  minimal return on capital for overall trade as a decimal
            minDaysToEarnings:  minimum number of days to put on trade before earnings
            minCredit:  minimum credit to collect on overall trade
            profitTargetPercent:  percentage of initial credit to use when closing trade
            customManagement:  boolean -- uses custom strategy to manage trade
            maxBidAsk:  maximum price to allow between bid and ask prices of option (for any strike or put/call)
            maxMidDev:  maximum deviation from midprice on opening and closing of trade (e.g., 0.02 cents from midprice)
            minDaysSinceEarnings:  minimum number of days to wait after last earnings before putting on strategy
            minIVR:  minimum implied volatility rank needed to put on strategy
            minBuyingPower:  minimum investment we want for the strategy -- since prices vary greatly over a range like
                             1990 to 2017, we would like to have the same amount of money in the market at any given
                             time, so we increase the number of contracts to reach this minBuyingPower
    """

    def __init__(self, eventQueue, optCallDelta, maxCallDelta, optPutDelta, maxPutDelta, startTime, buyOrSell,
                 underlying, orderQuantity, daysBeforeClose, expCycle=None, optimalDTE=None,
                 minimumDTE=None, roc=None, minDaysToEarnings=None, minCredit=None, profitTargetPercent=None,
                 customManagement=None, maxBidAsk=None, maxMidDev=None, minDaysSinceEarnings=None, minIVR=None,
                 minBuyingPower=None):

        #For arguments that are not supported or don't have implementations, we return an exception to prevent confusion
        if not roc == None:
            raise NotImplementedError, "Specifying ROC currently not supported"

        if not minDaysToEarnings == None or not minDaysSinceEarnings == None:
            raise NotImplementedError, "Ability to filter out dates with respect to earnings currently not supported"

        #if not customManagement == None:
        #    raise NotImplementedError, "Strategy for custom management not implemented / supported"

        if not minIVR == None:
            raise NotImplementedError, "Specifying implied volatility rank currently not implemented / supported"

        self.__eventQueue = eventQueue
        self.__strategy = "strangle"
        self.__optCallDelta = optCallDelta
        self.__maxCallDelta = maxCallDelta
        self.__optPutDelta = optPutDelta
        self.__maxPutDelta = maxPutDelta

        strategy.Strategy.__init__(self, startTime, self.__strategy, buyOrSell, underlying, orderQuantity,
                                   daysBeforeClose, expCycle, optimalDTE, minimumDTE, roc, minDaysToEarnings,
                                   minCredit, profitTargetPercent, customManagement, maxBidAsk, maxMidDev,
                                   minDaysSinceEarnings, minIVR, minBuyingPower)

        # For debugging open file
        #self._f = open('stranglesCreated', 'w')

    def getOptimalCallDelta(self):
        return self.__optCallDelta

    def getMaxCallDelta(self):
        return self.__maxCallDelta

    def getOptimalPutDelta(self):
        return self.__optPutDelta

    def getMaxPutDelta(self):
        return self.__maxPutDelta

    def checkForSignal(self, event):
        """Criteria that we need to check before generating a signal event:

        Params:
        event - tick data we parse through to determine if we want to create a strangle for the strategy

        Required:
        optCallDelta:  optimal delta for call, usually around 16 delta
        maxCallDelta:  max delta for call, usually around 30 delta
        optPutDelta:  optimal delta for put, usually around 16 delta
        maxPutDelta:  max delta for put, usually around 30 delta

        Optional:
        expCycle:  specifies if we want to do monthly ('m'); unspecified means we can do weekly, quarterly, etc
        optimalDTE:  optimal number of days before expiration to put on strategy
        minimumDTE:  minimum number of days before expiration to put on strategy
        roc:  minimal return on capital for overall trade as a decimal (not handled)
        minDaysToEarnings:  minimum number of days to put on trade before earnings (not handled)
        minCredit:  minimum credit to collect on overall trade (not handled)
        maxBidAsk:  maximum price to allow between bid and ask prices of option (for any strike or put/call)
        minDaysSinceEarnings:  minimum number of days to wait after last earnings before putting on strategy (not handled)
        minIVR:  minimum implied volatility rank needed to put on strategy (not handled)

        We go through each option in the option chain and find all of the options that meet the criteria.  If there
        are multiple options that meet the criteria, we choose the first one, but we could use some other type of
        rule for choosing.
        """

        # These variables will be used to keep track of the optimal options as we go through the options
        # chain
        optimalCallOpt = []
        optimalCallDTE = None
        optimalPutOpt = []
        optimalPutDTE = None
        studyDTE = self.getOptimalDTE()
        studyCallDelta = self.getOptimalCallDelta()
        studyPutDelta = self.getOptimalPutDelta()

        # Get the data from the tick event
        eventData = event.getData()

        # Process one option at a time from the option chain (now objects of option class)
        for option in eventData:

            # First check if the option is a call or a put
            if option.getOptionType() == 'CALL':
                if self.getExpCycle() == 'm':  # monthly options specified
                    if not self.isMonthlyExp(option.getDTE()):
                        continue

                # Check min DTE
                if not self.getMinimumDTE() == None:
                    if not self.hasMinimumDTE(option.getDateTime(), option.getDTE()):
                        continue

                # Check that call delta is less or equal to than max call delta specified
                if not option.getDelta() <= self.getMaxCallDelta():
                    continue

                # Check if bid / ask of option < maxBidAsk specific in strangle strategy
                if not self.getMaxBidAsk() == None:
                    if self.calcBidAskDiff(option.getBidPrice(), option.getAskPrice()) > self.getMaxBidAsk():
                        continue

                # Get current DTE in days
                currentDTE = self.getNumDays(option.getDateTime(), option.getDTE())

                # Check if DTE of current option is closer to optimal DTE we want
                if optimalCallDTE == None:
                    optimalCallDTE = currentDTE
                    optimalCallOpt = option
                # Check if there is a expiration closer to the study requested expiration
                elif abs(currentDTE - studyDTE) < abs(optimalCallDTE - studyDTE):
                    optimalCallDTE = currentDTE
                    optimalCallOpt = option
                #Option has same DTE as optimalCallOpt; check deltas
                elif (currentDTE - studyDTE) == (optimalCallDTE - studyDTE):
                    curDelta = option.getDelta()
                    optimalDelta = optimalCallOpt.getDelta()
                    if abs(curDelta - optimalDelta) < abs(studyCallDelta - optimalDelta):
                        optimalCallOpt = option

            elif option.getOptionType() == 'PUT':
                if self.getExpCycle() == 'm':  # monthly options specified
                    if not self.isMonthlyExp(option.getDTE()):
                        continue

                # Check min DTE
                if not self.getMinimumDTE() == None:
                    if not self.hasMinimumDTE(option.getDateTime(), option.getDTE()):
                        continue

                # Check that put delta is greater than or equal to max put delta specified
                if not option.getDelta() >= self.getMaxPutDelta():
                    continue

                # Check if bid / ask of option < maxBidAsk specific in strangle strategy
                if not self.getMaxBidAsk() == None:
                    if self.calcBidAskDiff(option.getBidPrice(), option.getAskPrice()) > self.getMaxBidAsk():
                        continue

                # Get current DTE in days
                currentDTE = self.getNumDays(option.getDateTime(), option.getDTE())

                # Check if DTE of current option is closer to optimal DTE we want
                if optimalPutDTE == None:
                    optimalPutDTE = currentDTE
                    optimalPutOpt = option
                # Check if there is a expiration closer to the study requested expiration
                elif abs(currentDTE - studyDTE) < abs(optimalPutDTE - studyDTE):
                    optimalPutDTE = currentDTE
                    optimalPutOpt = option
                # Option has same DTE as optimalPutOpt; check deltas to find closest to studyPutDelta
                elif currentDTE == optimalPutDTE:
                    curDelta = option.getDelta()
                    optimalDelta = optimalPutOpt.getDelta()
                    if abs(curDelta - optimalDelta) < abs(studyPutDelta - optimalDelta):
                        optimalPutOpt = option

        # Must check that a CALL and PUT were found which meet criteria and are in the same expiration
        if optimalPutOpt and optimalCallOpt and optimalPutOpt.getDTE() == optimalCallOpt.getDTE():
            # self._f.write("Date / Time {}".format(option.getDateTime()))
            # self._f.write("\n")
            # self._f.write("Put Delta {}, Put DTE {}".format(optimalPutOpt.getDelta(), optimalPutOpt.getDTE()))
            # self._f.write("\n")
            # self._f.write("Call Delta {}, Call DTE {}".format(optimalCallOpt.getDelta(), optimalCallOpt.getDTE()))
            # self._f.write("\n")
            # self._f.flush()
            # We create a strangle option primitive; the strangle primitive will have several of the
            # arguments from the init of StrangleStrat class
            strangleObj = strangle.Strangle(self.getOrderQuantity(), optimalCallOpt, optimalPutOpt, 'SELL',
                                            self.getDaysBeforeClose(), self.getProfitTargetPercent(),
                                            self.getCustomManagementFlag(), self.getMaxBidAsk(), self.getMaxMidDev())

            # If we are requiring that we always have the same amount of money invested regardless of time frame,
            # then we may need to increase the number of strangles to meet this minBuyingPower requirement.
            minBuyingPower = self.getMinBuyingPower()
            if minBuyingPower:
                buyingPowerUsed = strangleObj.getBuyingPower()
                # Require at least one contract; too much buying power will be rejected in the portfolio class
                numContractsToAdd = max(1, int(minBuyingPower / buyingPowerUsed))
                strangleObj.setNumContracts(numContractsToAdd)

            # Create signal event to put on strangle strategy and add to queue
            event = signalEvent.SignalEvent()
            event.createEvent(strangleObj)
            self.__eventQueue.put(event)

    def calcBidAskDiff(self, bidPrice, askPrice):
        '''
        Calculate the absolute difference between the bid and ask price
        If any of the arguments are <= 0, return a very large difference (100)
        :param bidPrice: price at which the option can be sold
        :param askPrice: price at which the option can be bought
        :return: absolute difference; 100 if bidPrice of askPrice are less than zero or NaN
        '''
        if self.isNumber(bidPrice) and self.isNumber(askPrice) and bidPrice > 0 and askPrice > 0:
            return abs(bidPrice - askPrice)
        else:
            return 100


    def isMonthlyExp(self, dateTime):
        '''
        Check if the option expiration falls on the third Friday of the month, or if the third Friday is a holiday,
        check if the expiration falls on the Thursday that preceeds it
        Technically, the option expires on a Saturday, so we need to subtract a day from the date and check if the day
        is the third friday of the month
        :param dateTime: option expiration date in mm/dd/yy format
        :return: true if it's a monthly option; false otherwise
        '''

        return (dateTime.weekday() == 4 and 14 < dateTime.day < 22)

    def hasMinimumDTE(self, curDateTime, expDateTime):
        '''
        Determine if the current expiration date of the option is >= self.minimumDTE days from the current date
        :param curDateTime: current date in mm/dd/yy format
        :param expDateTime: option expiration date in mm/dd/yy format
        :return: true if difference between current date and dateTime is >= self.minimumDTE; else false
        '''
        return (expDateTime - curDateTime).days >= self.getMinimumDTE()

    def getNumDays(self, curDateTime, expDateTime):
        '''
        Determine the number of days between the curDateTime and the expDateTime
        :param curDateTime: current date in mm/dd/yy format
        :param expDateTime: option expiration date in mm/dd/yy format
        :return: number of days between curDateTime and expDateTime
        '''
        return (expDateTime - curDateTime).days

    def isNumber(self, s):
        '''
        Check if string is a number
        :return: True if string is a number; False otherwise
        '''
        try:
            float(s)
            return True
        except ValueError:
            return False