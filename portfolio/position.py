
class Position(object):
    """This class creates statistics for invidual positions inside of a portfolio

       Position intrinsics:
       PLopen:  current value of positions in dollars (positive or negative)
       PLday:  amount of money gained / lost for position in the current day in dollars (positive or negative)
       PLopenPercent:  same as PLopen, but expressed as a percent of total capital being used
       PLdayPecent:  same as PLday, but expressed as a percentage of total capital being used

    """

    def __init__(self):
        self.__PLopen = None
        self.__PLday = None
        self.__PLopenPercent = None
        self.__PLdayPercent = None