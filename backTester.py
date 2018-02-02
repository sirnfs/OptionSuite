import Queue as queue
from dataHandler import csvData
from strategyManager import strangleStrat
from portfolioManager import portfolio
from datetime import datetime
import pytz
import logging
"""
This file contains a basic strategy example, and can be though of 
as an end-to-end test of the whole Backtester project
In this example, we actually backtest a strategy and do not use
the suite for live trading
"""

class BackTestSession(object):
    """Class for holding all parameters of backtesting session"""

    def __init__(self):

        #Parameters for CSV data for backtesting session
        inputDir = './sampleData'
        fileSource = 'aapl_sample_ivolatility.csv'
        dataProvider = 'iVolatility'
        self.eventQueue = queue.Queue()
        self.dataHandler = csvData.CsvData(inputDir, fileSource, dataProvider, self.eventQueue)

        #Parameters for strangle strategy -- TODO: move params to file
        optCallDelta = 16 #integers or floats?
        maxCallDelta = 30
        optPutDelta = 16
        maxPutDelta = 30
        startTime = datetime.now(pytz.utc)
        buyOrSell = 1 #0 = buy, 1 = sell (currently only support selling)
        underlying = 'AAPL'
        orderQuantity = 1
        daysBeforeClose = 5
        optimalDTE = 45
        minimumDTE = 25
        minCredit = 0.5
        profitTargetPercent = 50
        maxBidAsk = 0.05
        minDaysToEarnings = 25
        minDaysSinceEarnings = 3
        minIVR = 15
        self.strategyManager = strangleStrat.StrangleStrat(self.eventQueue, optCallDelta, maxCallDelta, optPutDelta,
                                                           maxPutDelta, startTime, buyOrSell, underlying,
                                                           orderQuantity, daysBeforeClose, optimalDTE=optimalDTE,
                                                           minimumDTE=minimumDTE, minDaysToEarnings=minDaysToEarnings,
                                                           minCredit=minCredit, profitTargetPercent=profitTargetPercent,
                                                           maxBidAsk=maxBidAsk,
                                                           minDaysSinceEarnings=minDaysSinceEarnings, minIVR=minIVR)

        startingCapital = 100000
        maxCapitalToUse = 0.5
        maxCapitalToUsePerTrade = 0.05
        self.portfolioManager = portfolio.Portfolio(startingCapital, maxCapitalToUse, maxCapitalToUsePerTrade)

def run(session):

    while (1):  #Infinite loop to keep processing items in queue
        try:
            event = session.eventQueue.get(False)
        except queue.Empty:
            #Get data for tick event
            session.dataHandler.getNextTick()
        else:
            if event is not None:
                if event.type == 'TICK':
                    #self.cur_time = event.time
                    session.strategyManager.checkForSignal(event)
                    session.portfolioManager.updatePortfolio(event)
                elif event.type == 'SIGNAL':
                    session.portfolioManager.onSignal(event)
                elif event.type == 'ORDER':
                    pass
                    #self.execution_handler.execute_order(event)
                elif event.type == 'FILL':
                    pass
                    #self.portfolio_handler.on_fill(event)
                else:
                    raise NotImplemented("Unsupported event.type '%s'" % event.type)


if __name__ == "__main__":

    # Set up logging for the session
    logging.basicConfig(filename='session.log', level=logging.DEBUG)

    #Create a session and configure the session
    session = BackTestSession()

    #Create a backtester run
    run(session)