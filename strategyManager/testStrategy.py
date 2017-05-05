import Queue as queue
from dataHandler import csvData

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
        inputDir = '../sampleData'
        fileSource = 'aapl_sample_ivolatility.csv'
        dataProvider = 'iVolatility'
        self.eventQueue = queue.Queue()
        self.dataHandler = csvData.CsvData(inputDir, fileSource, dataProvider, self.eventQueue)
        #All of the configuration / settings for the strategy are in the class itself
        #self.strategyManger = strangleStrategy()
        #self.__portfolio = portfolio()
        #self.__orderExecution = orderExecution()
        #self.__riskManagement = riskManagement()


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
                    pass
                    #self.cur_time = event.time
                    #self.strategyManager.checkForSignal(event)
                    #self.portfolio_handler.update_portfolio_value()
                    #self.statistics.update(event.time, self.portfolio_handler)
                elif event.type == 'SIGNAL':
                    pass
                    #self.riskManager.checkRisk(event)
                    #self.portfolio_handler.on_signal(event)
                elif event.type == 'ORDER':
                    pass
                    #self.execution_handler.execute_order(event)
                elif event.type == 'FILL':
                    pass
                    #self.portfolio_handler.on_fill(event)
                else:
                    raise NotImplemented("Unsupported event.type '%s'" % event.type)


if __name__ == "__main__":

    #Create a session and configure the session
    session = BackTestSession()

    #Create a backtester run
    run(session)