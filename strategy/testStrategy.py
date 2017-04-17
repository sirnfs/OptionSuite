"""
This file contains a basic strategy example, and can be though of 
as an end-to-end test of the whole Backtester project
In this example, we actually backtest a strategy and do not use
the suite for live trading
"""

def run():
    """
    Sets up all the required classes to create a backtester run
    """
    #Create the event queue
    eventQ = Event()
    eventQ.createQueue()


if __name__ == "__main__":

    #Create a backtester run
    run()