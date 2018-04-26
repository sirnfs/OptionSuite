import option
import logging

class Call(option.Option):
    """This class defines a CALL option, which inherits from the Option class."""
    def __init__(self, underlyingTicker, strikePrice, delta, DTE, longOrShort=None, underlyingPrice=None,
                 underlyingTradePrice=None, optionSymbol=None, optionAlias=None, bidPrice=None, askPrice=None,
                 tradePrice=None, openInterest=None, volume=None, dateTime=None, theta=None, gamma=None, rho=None,
                 vega=None, impliedVol=None, exchangeCode=None, exercisePrice=None, assignPrice=None, openCost=None,
                 closeCost=None):

        __optionType = "CALL"

        option.Option.__init__(self, underlyingTicker, strikePrice, __optionType, delta, DTE, longOrShort,
                               underlyingPrice, underlyingTradePrice, optionSymbol, optionAlias, bidPrice, askPrice,
                               tradePrice, openInterest, volume, dateTime, theta, gamma, rho, vega, impliedVol,
                               exchangeCode, exercisePrice, assignPrice, openCost, closeCost)

    def updateIntrinsics(self, newOpt):
        """Update the relevant values of the original option with those of the new option; e.g., update price, delta
        :param newOpt: new option from the latest tick.
        """
        self.setUnderlyingPrice(newOpt.getUnderlyingPrice())
        self.setBidPrice(newOpt.getBidPrice())
        self.setAskPrice(newOpt.getAskPrice())
        self.setOpenInterest(newOpt.getOpenInterest())
        self.setOptionVolume(newOpt.getOptionVolume())
        self.setDateTime(newOpt.getDateTime())
        self.setDelta(newOpt.getDelta())
        self.setTheta(newOpt.getTheta())
        self.setGamma(newOpt.getGamma())
        self.setRho(newOpt.getRho())
        self.setVega(newOpt.getVega())
        self.setImpliedVol(newOpt.getImpliedVol())

        # Some debugging prints
        logging.info('Date / time: %s', self.getDateTime())
        logging.info('DTE: %s', self.getDTE())
