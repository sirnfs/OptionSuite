import dataclasses
from base import option


@dataclasses.dataclass
class Call(option.Option):
    """This class defines a CALL option, which inherits from the Option class."""
    optionType: option.OptionTypes = option.OptionTypes.CALL
