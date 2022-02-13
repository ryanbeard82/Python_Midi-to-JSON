from dataclasses import dataclass
from typing import List


@dataclass
class JSON_Notes():
    """
    This class stores the 3 expected JSON note parameters intended to be declared as list variables, one for each wave channel.
    """
    value: int = 0
    octave: int = 0
    length: int = 0

    def compile(self) -> List[int]:
        return [self.value, self.octave, self.length]
