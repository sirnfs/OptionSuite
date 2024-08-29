import abc
from optionPrimitives import optionPrimitive


class RiskManagement(abc.ABC):
    """This class is a generic type for handling risk management strategies."""

    @abc.abstractmethod
    def managePosition(self, currentPosition: optionPrimitive) -> bool:
        """Manages the current position in the portfolio.
        Managing the position means indicating whether the position should be removed from the portfolio.
        In addition, we could create another signalEvent here if we want to do something like roll the strategy to
        the next month.

        :param currentPosition: Current position in the portfolio.
        """
        pass

    def getRiskManagementType(self) -> int:
        """Returns the risk management type being used."""
        pass
