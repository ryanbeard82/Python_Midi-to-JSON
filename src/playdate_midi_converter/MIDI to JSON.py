import os
import sys
from mido.midifiles.midifiles import MidiFile
import logging

from playdate_midi_converter.encode import Converter

logging.basicConfig(level=logging.DEBUG)

# Set constants & Global Variables
DEV_MODE = True
SYNTH_CHANNELS = ["Sine", "Square", "Sawtooth", "Triangle", "Noise", "Ignore Track"]
MAX_NOTES = 512

songBPM = 0
ticksPerBeat = 0
sixteenthNoteDefault = 0
songTicks = 0


def main():
    # main subroutine
    
    # identify globals
    global songBPM
    global ticksPerBeat
    global sixteenthNoteDefault
    global songTicks
    
    # have the user select a MIDI file
    # or if DEV_MODE constant is set to "True", use
    # the Demo File contained in the project
    if DEV_MODE:
        dirName = os.path.dirname(os.path.realpath("__file__"))
        fileName = os.path.join(dirName, "Demo Files/simple_sample.mid")
    else:
        fileName = open_file()
        dirName = os.path.dirname(fileName)
    
    # validate selection
    if fileName is None:
        print("No file selected. Exiting application.")
        exit()
    
    # capture as a midifile   
    yourMidiFile = MidiFile(fileName, clip=True)
    
    converter = Converter()
    userSong = converter.convert(yourMidiFile)

    # print song data to file
    converter.write_json_file(fileName, userSong)
    
    sys.exit("Exiting application.")

































main()
