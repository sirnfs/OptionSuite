from event import TickEvent
import Queue as queue
from dataHandler import csvData

"""
This file contains a basic strategy example, and can be though of 
as an end-to-end test of the whole Backtester project
In this example, we actually backtest a strategy and do not use
the suite for live trading
"""





#TODO:  data source should be such that we can call getNextTick without knowing
#anything abut the data source, which means that there will be a configuration
#step to set up the data source first, which should be handled in the Session object




class Session(object):
    """Class for holding all parameters of strategy / session"""

    def __init__(self, dataSource, eventQueue):
        self.__dataSource = dataSource
        self.__eventQueue = eventQueue


def run():
    """
    Sets up all the required classes to create a backtester run
    """
    #Create the event queue
    eventQ = queue.Queue()

    #For this test / example, we will do a backtesting using an input CSV
    csvObj = csvData.CsvData('./sampleData')
    dataProvider = 'iVolatility'
    csvObj.openDataSource('aapl_sample_ivolatility.csv', dataProvider)

    #while (1):  #Infinite loop to keep processing items in queue
    #     try:
    #         event = eventQ.get(False)
    #     except queue.Empty:
        #     createTickEvent(event])





if __name__ == "__main__":

    #Create a backtester run
    run()