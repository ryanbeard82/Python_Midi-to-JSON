from tkinter.filedialog import askopenfilename, askdirectory
from pathlib import Path
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


def choose_save_dir(context: Context, initial_dir: str):
    """Use tkinter to choose a save directory."""
    if initial_dir is None:
        initial_dir = str(Path.home())
    save_dir = askdirectory(
        initialdir=initial_dir,
        mustexist=True,
        title="Choose save directory for JSON file."
        )
    if save_dir:
        return save_dir
    else:
        context.get_logger('save_file').info('Cancelled')
        return None


