import enum
from riskManager import riskManagement
from optionPrimitives import optionPrimitive
from typing import Optional


class PutVerticalManagementStrategyTypes(enum.Enum):
    HOLD_TO_EXPIRATION = 0
    CLOSE_AT_50_PERCENT = 1
    CLOSE_AT_50_PERCENT_OR_21_DAYS = 2
    CLOSE_AT_50_PERCENT_OR_21_DAYS_OR_HALFLOSS = 3
    CLOSE_AT_21_DAYS = 4


class PutVerticalRiskManagement(riskManagement.RiskManagement):
    """This class handles risk management strategies for put verticals."""

    def __init__(self, managementType: PutVerticalManagementStrategyTypes, closeDuration: Optional[int]) -> None:
        """This class handles the risk management for the put vertical.

        Attributes:
          managementType: predetermined management strategies.
          closeDuration: number of days from expiration to close the trade.
        """
        self.__managementType = managementType
        self.__closeDuration = closeDuration

    def managePosition(self, currentPosition: optionPrimitive) -> bool:
        """Manages the current position in the portfolio.
        Managing the position means indicating whether the position should be removed from the portfolio.
        In addition, we could create another signalEvent here if we want to do something like roll the strategy to
        the next month.

        :param currentPosition: Current position in the portfolio.
        """
        if self.__closeDuration is not None:
            # Closes position out when number of days left is equal to closeDuration.
            if currentPosition.calcProfitLossPercentage() >= 50 or (
               currentPosition.getNumberOfDaysLeft() == self.__closeDuration):
                return True
            # This is a backup if an option is chosen where numberofdaysleft < 21.
            if currentPosition.getNumberOfDaysLeft() <= 1:
                # Indicates that the options are expiring on (or near) this date.
                return True
        elif self.__managementType == PutVerticalManagementStrategyTypes.HOLD_TO_EXPIRATION:
            # Setting this to '1' since I've been using SPX data, which has European style options where trading ends
            # the day before expiration.
            if currentPosition.getNumberOfDaysLeft() <= 1:
                # Indicates that the options are expiring on (or near) this date.
                return True
        elif self.__managementType == PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT:
            if currentPosition.calcProfitLossPercentage() >= 50:
                return True
            if currentPosition.getNumberOfDaysLeft() <= 1:
                # Indicates that the options are expiring on (or near) this date.
                return True
        elif self.__managementType == PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS:
            if currentPosition.calcProfitLossPercentage() >= 50 or currentPosition.getNumberOfDaysLeft() == 21:
                return True
            # This is a backup in an option is chosen where numberofdaysleft < 21.
            if currentPosition.getNumberOfDaysLeft() <= 1:
                # Indicates that the options are expiring on (or near) this date.
                return True
        elif self.__managementType == PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS_OR_HALFLOSS:
            if currentPosition.calcProfitLossPercentage() >= 50 or currentPosition.getNumberOfDaysLeft() == 21 or (
               currentPosition.calcProfitLossPercentage() <= -50):
                return True
            if currentPosition.getNumberOfDaysLeft() <= 1:
                # Indicates that the options are expiring on (or near) this date.
                return True
        elif self.__managementType == PutVerticalManagementStrategyTypes.CLOSE_AT_21_DAYS:
            if currentPosition.getNumberOfDaysLeft() == 21:
                return True
            if currentPosition.getNumberOfDaysLeft() <= 1:
                # Indicates that the options are expiring on (or near) this date.
                return True
        else:
            raise NotImplementedError('No management strategy was specified or has not yet been implemented.')
        return False

    def getRiskManagementType(self) -> PutVerticalManagementStrategyTypes:
        """Returns the risk management type being used."""
        return self.__managementType
