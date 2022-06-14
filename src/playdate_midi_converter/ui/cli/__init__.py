from typing import TextIO as _TextIO, Union as _Union
from sys import stdin as _stdin, stdout as _stdout, stderr as _stderr

try:
    from enum import StrEnum
except ImportError:
    from playdate_midi_converter.strenum import StrEnum


class TextColor(StrEnum):
    """https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    BOLD_OFF = '\033[21m'
    UNDERLINE = '\033[4m'
    UNDERLINE_OFF = '\033[24m'


class UserIO(object):
    def __init__(self, user_in: _TextIO = _stdin, user_out: _TextIO = _stdout, err_out: _TextIO = _stderr):
        super().__init__()
        self.user_in = user_in
        self.user_out = user_out
        self.err_out = err_out
    
    def print(self, *msgs: _Union[str, TextColor]):
        self.user_out.write(''.join(msgs))
        self.user_out.flush()
    
    def read_line(self, msg: str) -> str:
        self.print(msg)
        return self.user_in.readline().strip()
    
    def yes_no(self, msg: str, default_yes: bool = True) -> bool:
        if default_yes:
            choices = '[Y/n]'
        else:
            choices = '[y/N]'
        while True:
            choice = self.read_line(f"{msg} {TextColor.BOLD}{choices}{TextColor.ENDC} ")
            if (choice or 'y').lower().startswith('y'):
                return True
            if choice.lower().startswith('n'):
                return False
