from ast import Constant
from fileinput import filename
from itertools import count
from operator import countOf
from turtle import title
from mido import MidiFile
from tkinter import *
from pathlib import Path
from tkinter.filedialog import askopenfilename, asksaveasfile, askdirectory
from JSON_Elements import *
from pick import pick
import logging
from MIDI_Elements.MIDI_Track import MIDI_Track
import os

logging.basicConfig(level=logging.DEBUG)

# Set constants & Global Variables
DEV_MODE = True
SYNTH_CHANNELS = ["Sine","Square","Sawtooth","Triangle","Noise","Ignore Track"]

def main():
    # main subroutine
    
    # used to divid note lengths if
    # values smaller than 1/6 note are used
    noteMultiplier = 0.0
    
    # have the user select a MIDI file
    # or if DEV_MODE constant is set to "True", use
    # the Demo File contained in the project
    if DEV_MODE:
        dirname = os.path.dirname(os.path.realpath("__file__"))
        fileName = os.path.join(dirname,"Demo Files/FartyBird_Score.mid")
    else:
        fileName = open_file()
    
    # validate selection
    if fileName is None:
        print("No file selected. Exiting application.")
        exit()
    
    # capture as a midifile   
    yourMidiFile = MidiFile(fileName,clip=True)
    
    logging.info("Selected MIDI Filename: " + yourMidiFile.filename)
    
    # get bpm info
    songBPM = round(yourMidiFile.ticks_per_beat/6)
    logging.info("MIDI Ticks per beat: " + str(yourMidiFile.ticks_per_beat))
    logging.info("MIDI BPM: " + str(songBPM))
    
    # evaluate tracks
    midiTracks = getTracks(yourMidiFile)
    
    # assign pulp synth channels
    getTrackMapping(midiTracks)
    
    for track in midiTracks:
        print(str(track.track_number) + " - " + track.track_name + " is mapped to " + track.synth_channel)
    
def getTrackMapping(midi_tracks: MIDI_Track) -> MIDI_Track:
    # use "pick" to collect MIDI track mapping
    # to Pulp synth channels from the user via Terminal
    
    availableSynthList = SYNTH_CHANNELS
    trackNumber = 0
    print("You must map each MIDI track to one of Pulp's 5 synth engines.")
    while trackNumber < len(midi_tracks):
        mappingPrompt = "Please select an engine for " + midi_tracks[trackNumber].track_name
        synthOptions = availableSynthList
        selectedSynth, selectedIndex = pick(synthOptions,mappingPrompt)
        
        logging.info("User selected " + selectedSynth + " for Track " + str(midi_tracks[trackNumber].track_number) + " - " + midi_tracks[trackNumber].track_name)
        
        if selectedSynth != "Ignore Track":
            midi_tracks[trackNumber].synth_channel = selectedSynth
            synthOptions.remove(selectedSynth)
        
        trackNumber += 1
    
def getTracks(midi_file: MidiFile) -> MIDI_Track:
    # collects track data from MIDI file
    # and stores it in a list of MIDI Tracks
    
    newTrackCollection = []
    newTrack = None
    
    for i, track in enumerate(midi_file.tracks):
        
        if i != 0:
            newTrack = MIDI_Track(i,track,track.name)
            newTrackCollection.append(newTrack)
            logging.info ("Track {}: {}".format(i,track.name))
            
    return newTrackCollection
    
def open_file():
    # using tkinter to provide native file selection dialog
    
    file = askopenfilename(filetypes=(("Midi Files", "*.mid"),
                                       ("All files", "*.*")),
                           title="Open MIDI File",
                           initialdir=str(Path.home()))
    if file:
        return file
    else:
        logging.info("Cancelled")
        return None
    
main()