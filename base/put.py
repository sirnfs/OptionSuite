import dataclasses
from base import option

@dataclasses.dataclass
class Put(option.Option):
  """This class defines a PUT option, which inherits from the Option class."""
  optionType: option.OptionTypes = option.OptionTypes.PUT
