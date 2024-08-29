import enum
from riskManager import riskManagement
from optionPrimitives import optionPrimitive


class StrangleManagementStrategyTypes(enum.Enum):
    HOLD_TO_EXPIRATION = 0
    CLOSE_AT_50_PERCENT = 1
    CLOSE_AT_50_PERCENT_OR_21_DAYS = 2


class StrangleRiskManagement(riskManagement.RiskManagement):
    """This class handles risk management strategies for strangles."""

    def __init__(self, managementType: StrangleManagementStrategyTypes) -> None:
        self.__managementType = managementType

    def managePosition(self, currentPosition: optionPrimitive) -> bool:
        """Manages the current position in the portfolio.
        Managing the position means indicating whether the position should be removed from the portfolio. In addition,
        we could create another signalEvent here if we want to do something like roll the strategy to the next month.

        :param currentPosition: Current position in the portfolio.
        """
        if self.__managementType == StrangleManagementStrategyTypes.HOLD_TO_EXPIRATION:
            # Setting this to '1' since I've been using SPX data, which has European style options where trading ends
            # the day before expiration.
            if currentPosition.getNumberOfDaysLeft() <= 1:
                # Indicates that the options are expiring on (or near) this date.
                return True
        elif self.__managementType == StrangleManagementStrategyTypes.CLOSE_AT_50_PERCENT:
            if currentPosition.calcProfitLossPercentage() >= 50:
                return True
            if currentPosition.getNumberOfDaysLeft() <= 1:
                return True
        elif self.__managementType == StrangleManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS:
            if currentPosition.calcProfitLossPercentage() >= 50 or currentPosition.getNumberOfDaysLeft() == 21:
                return True
            if currentPosition.getNumberOfDaysLeft() <= 1:
                return True
        else:
            raise NotImplementedError('No management strategy was specified or has not yet been implemented.')
        return False

    def getRiskManagementType(self) -> StrangleManagementStrategyTypes:
        """Returns the risk management type being used."""
        return self.__managementType
