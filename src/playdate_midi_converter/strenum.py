from enum import Enum as _Enum


class StrEnum(str, _Enum):
    """Shiv class to add support for StrEnums in python versions >= 3.6 and <3.10"""
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name
    
    def __str__(self):
        return self.value
