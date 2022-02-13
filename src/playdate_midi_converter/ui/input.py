from tkinter.filedialog import askopenfilename
from pick import pick

from playdate_midi_converter.config import Context


def choose(context: Context, message, options):
    log = context.get_logger('choose')
    chosen = pick(options, message)
    log.info(f"{message} : {chosen}")
    return chosen


def open_file(context: Context):
    """using tkinter to provide native file selection dialog"""

    file = askopenfilename(filetypes=(
            ("Midi Files", "*.mid"),
            ("All files", "*.*")
        ),
        title="Open MIDI File",
        initialdir=str(Path.home()))
    if file:
        return file
    else:
        context.get_logger('open_file').info("Cancelled")
        return None
