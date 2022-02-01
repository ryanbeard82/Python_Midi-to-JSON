from ntpath import join
import os
import sys
from ast import Constant
from fileinput import filename
from itertools import count
from operator import countOf
from telnetlib import theNULL
from turtle import title
from unittest import case
from mido import MidiFile
from mido import MetaMessage
from mido import tempo2bpm
from tkinter import *
from pathlib import Path
from tkinter.filedialog import askopenfilename, asksaveasfile, askdirectory
from pick import pick
import logging
from JSON_Elements.JSON_Songs import JSON_Songs
from JSON_Elements.JSON_Notes import JSON_Notes
from MIDI_Elements.MIDI_Track import MIDI_Track

logging.basicConfig(level=logging.DEBUG)

# Set constants & Global Variables
DEV_MODE = True
SYNTH_CHANNELS = ["Sine","Square","Sawtooth","Triangle","Noise","Ignore Track"]
MAX_NOTES = 512

songBPM = 0
ticksPerBeat = 0
sixteenthNoteDeafalt = 0
noteMultiplier = 0
songTicks = 0

def main():
    # main subroutine
    
    #identify globals
    global songBPM
    global ticksPerBeat
    global sixteenthNoteDeafalt
    global noteMultiplier
    global songTicks
    
    # have the user select a MIDI file
    # or if DEV_MODE constant is set to "True", use
    # the Demo File contained in the project
    if DEV_MODE:
        dirName = os.path.dirname(os.path.realpath("__file__"))
        fileName = os.path.join(dirName,"Demo Files/simple_sample.mid")
    else:
        fileName = open_file()
        dirName = os.path.dirname(filename)
    
    # validate selection
    if fileName is None:
        print("No file selected. Exiting application.")
        exit()
    
    # capture as a midifile   
    yourMidiFile = MidiFile(fileName,clip=True)
    
    logging.info("Selected MIDI Filename: " + yourMidiFile.filename)
    
    # get bpm and clock info
    songBPM = getMIDI_BPM(yourMidiFile)
    ticksPerBeat = yourMidiFile.ticks_per_beat
    sixteenthNoteDeafalt = ticksPerBeat/4
    
    # TODO: Evaluate all messages for lowest msg.time, then update noteMultiplier / BPM
    # TODO: Join MIDI Tracks by Instrument (e.g. to handle Logic Regions on Export)
    
    logging.info("MIDI Ticks per beat: " + str(yourMidiFile.ticks_per_beat))
    logging.info("MIDI BPM: " + str(songBPM))
    
    # evaluate tracks
    midiTracks = getTracks(yourMidiFile)
    
    # assign pulp synth channels
    tracksAssigned = getTrackMapping(midiTracks)
    
    # exit if the user did not assign any tracks
    if not tracksAssigned:
        sys.exit("No tracks assigned. Exiting application.")
    
    # create new song if the user has assigned track maps
    songName = input("Enter your song's name:")
    userSong = JSON_Songs(0,songBPM,songName)
    
    # evaluate notes for each track and assign to song
    for track in midiTracks:
        print(str(track.track_number) + " - " + track.track_name + " is mapped to " + track.synth_channel)
        if track.synth_channel == "Sine":
            userSong.sineNotes = getNotes(track.midi_data)
            if songTicks > userSong.ticks:
                userSong.ticks = songTicks
        elif track.synth_channel == "Square":
            userSong.squareNotes = getNotes(track.midi_data)
            if songTicks > userSong.ticks:
                userSong.ticks = songTicks
        elif track.synth_channel == "Sawtooth":
            userSong.sawNotes = getNotes(track.midi_data)
            if songTicks > userSong.ticks:
                userSong.ticks = songTicks
        elif track.synth_channel == "Triangle":
            userSong.triNotes = getNotes(track.midi_data)
            if songTicks > userSong.ticks:
                userSong.ticks = songTicks
        elif track.synth_channel == "Noise":
            userSong.noiseNotes = getNotes(track.midi_data)
            if songTicks > userSong.ticks:
                userSong.ticks = songTicks
    
    # print song data to file
    writeJSONfile(fileName,userSong)
    
    sys.exit("Exiting application.")

def getMIDI_BPM(midiFile: MidiFile) -> int:
    # convert tempo to BPM
    
    #set default BPM just in case
    bpm = 80
    
    for msg in midiFile.tracks[0]:
        if msg.type == "set_tempo":
            bpm = round(tempo2bpm(msg.tempo))
            return bpm
    
    return bpm

def writeJSONfile (inputFile: str,JSON_Song: JSON_Songs):
    # write user song data into JSON format
    # save file in input MIDI file directory
    
    outputFile = os.path.splitext(inputFile)[0]
    outputFile = outputFile + ".json"
    fileCopyCount = 1
    
    while os.path.exists(outputFile):
        outputFile = os.path.splitext(inputFile)[0]
        outputFile = outputFile + "_" + str(fileCopyCount) + ".json"
        fileCopyCount += 1
    
    f = open(outputFile,"a")
    
    # write pre-note content
    outputString = (
        ",".join((
            '[{"id":' + str(JSON_Song.id),
            '"bpm":' + str(JSON_Song.bpm),
            '"name":"' + JSON_Song.name + '"',
            '"notes":'
            ))
    )
    
    f.write(outputString)
    
    # write note content
    outputString = writeJSONnotes(JSON_Song)
    
    f.write(outputString)
    
    # write post-note content
    outputString = (
        ",".join((
            '"ticks":' + str(JSON_Song.ticks),
            '"splits":' + JSON_Song.splits,
            '"loopFrom":' + str(JSON_Song.loopFrom)
            ))
    )
    
    outputString = outputString + "}]"
    
    f.write(outputString)
    
    f.close()
    
    print("JSON file written and saved to " + outputFile)
    
def writeJSONnotes(JSON_Song: JSON_Songs) -> str:
    # function to capture notes from the JSON_Songs object
    # and write to text string for output

    noteString = "[["
    
    if JSON_Song.sineNotes != None:
        for i,note in enumerate(JSON_Song.sineNotes):
            if i == 0:
                noteString = noteString + ",".join((str(note.value),str(note.octave),str(note.length)))
            else:
                noteString = ",".join((noteString,str(note.value),str(note.octave),str(note.length)))
            
    noteString = noteString + "],["
    
    if JSON_Song.squareNotes != None:
        for i,note in enumerate(JSON_Song.squareNotes):
            if i == 0:
                noteString = noteString + ",".join((str(note.value),str(note.octave),str(note.length)))
            else:
                noteString = ",".join((noteString,str(note.value),str(note.octave),str(note.length)))
            
    noteString = noteString + "],["
    
    if JSON_Song.sawNotes != None:
        for i,note in enumerate(JSON_Song.sawNotes):
            if i == 0:
                noteString = noteString + ",".join((str(note.value),str(note.octave),str(note.length)))
            else:
                noteString = ",".join((noteString,str(note.value),str(note.octave),str(note.length)))
            
    noteString = noteString + "],["
    
    if JSON_Song.triNotes != None:
        for i,note in enumerate(JSON_Song.triNotes):
            if i == 0:
                noteString = noteString + ",".join((str(note.value),str(note.octave),str(note.length)))
            else:
                noteString = ",".join((noteString,str(note.value),str(note.octave),str(note.length)))
            
    noteString = noteString + "],["
    
    if JSON_Song.noiseNotes != None:
        for i,note in enumerate(JSON_Song.noiseNotes):
            if i == 0:
                noteString = noteString + ",".join((str(note.value),str(note.octave),str(note.length)))
            else:
                noteString = ",".join((noteString,str(note.value),str(note.octave),str(note.length)))
            
    noteString = noteString + "]],"
    
    return noteString

def getNotes(midiTrack: MIDI_Track) -> JSON_Notes:
    # get all the notes from a midi track and store in a JSON_Notes object
    
    global songTicks
    
    convertedMIDINotes = []
    noteCounter = 0
    deltaTime = 0
    lastNote = 0
    lastNoteIndex = 0

    for msg in midiTrack:
        
        if noteCounter == 512:
            # hit the max JSON song length - need to truncate
            logging.info("Max song length reached. Truncating song.")
            songTicks = noteCounter
            return convertedMIDINotes
            
        if not msg.is_meta:
            if msg.type == "note_on":
                # handling polyphony - not supported on playdate
                if lastNote != 0:
                    deltaTime += msg.time
                else:
                    if msg.time != 0:
                        restEvents = int(msg.time / sixteenthNoteDeafalt)
                        while restEvents != 0:
                            # add empty events for rest positions
                            newJSONnote = JSON_Notes(0,0,0)
                            convertedMIDINotes.append(newJSONnote)
                            noteCounter += 1
                            restEvents -= 1
                            
                    lastNote = msg.note
                    deltaTime = 0
                    noteValue = getNoteValue(msg.note)
                    noteOctave = getNoteOctave(msg.note)
                    noteLen = 1
                    newJSONnote = JSON_Notes(noteValue,noteOctave,noteLen)
                    convertedMIDINotes.append(newJSONnote)
                    lastNoteIndex = noteCounter
                    noteCounter += 1
                        
            elif msg.type == "note_off" and lastNote == msg.note:
                lastNote = 0
                deltaTime += msg.time

                noteLen = getNoteLength(deltaTime)
                convertedMIDINotes[lastNoteIndex].length = noteLen
                
                if deltaTime / sixteenthNoteDeafalt >= 2:
                    # add empty events for sustained note durations
                    restEvents = int(deltaTime / sixteenthNoteDeafalt)
                    restEvents -= 1 # accounts for note data already stored above
                    
                    while restEvents != 0:
                        # add empty events for rest positions
                        newJSONnote = JSON_Notes(0,0,0)
                        convertedMIDINotes.append(newJSONnote)
                        noteCounter += 1
                        restEvents -= 1
        else: # capture channel_prefix for delayed start time
            if msg.type == "channel_prefix" and msg.time > 0:
                restEvents = int(msg.time / sixteenthNoteDeafalt)
                while restEvents != 0:
                    # add empty events for rest positions
                    newJSONnote = JSON_Notes(0,0,0)
                    convertedMIDINotes.append(newJSONnote)
                    noteCounter += 1
                    restEvents -= 1
                                        
    songTicks = noteCounter
    return convertedMIDINotes

def getNoteValue(noteInt: int) -> int:
    # converts MIDI note to JSON note value
    
    noteValue = noteInt % 12 # 12 note scale
    noteValue += 1 # JSON format is a 1-based index
    
    return noteValue

def getNoteOctave(noteInt: int) -> int:
    #  gest the JSON note octave from MIDI note value
    
    if noteInt >= 24:
        noteOctave = int(noteInt / 12) # divide by 12 and round down
        noteOctave -= 2
    else:
        noteOctave = 0 # anything below octave 0 is set to 0
    
    return noteOctave
    
def getNoteLength(noteTime: int) -> int:
    # gets JSON note length (in 16ths) from MIDI note time
    
    if noteTime < sixteenthNoteDeafalt:
        noteLen = 1
    else:
        noteLen = int(noteTime / sixteenthNoteDeafalt)
    
    return noteLen

def getTrackMapping(midi_tracks: MIDI_Track) -> bool:
    # use "pick" to collect MIDI track mapping
    # to Pulp synth channels from the user via Terminal
    
    trackValidator = False
    availableSynthList = SYNTH_CHANNELS
    trackNumber = 0
    print("You must map each MIDI track to one of Pulp's 5 synth engines.")
    while trackNumber < len(midi_tracks):
        mappingPrompt = "Please select an engine for " + midi_tracks[trackNumber].track_name
        synthOptions = availableSynthList
        selectedSynth, selectedIndex = pick(synthOptions,mappingPrompt)
        
        logging.info("User selected " + selectedSynth + " for Track " + str(midi_tracks[trackNumber].track_number) + " - " + midi_tracks[trackNumber].track_name)
        
        if selectedSynth != "Ignore Track":
            trackValidator = True
            midi_tracks[trackNumber].synth_channel = selectedSynth
            synthOptions.remove(selectedSynth)
        
        trackNumber += 1
    
    return trackValidator
    
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