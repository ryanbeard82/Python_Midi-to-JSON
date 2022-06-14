from typing import Union, List, Tuple, IO
from io import IOBase
# import logging

from mido.midifiles.midifiles import MidiFile
from mido.midifiles.tracks import MidiTrack
from mido.midifiles.units import tempo2bpm

from playdate_midi_converter.song import Song, Track, Note
from playdate_midi_converter.config import Context


class Midi(object):
    context: Context
    
    def __init__(self, context: Context, file: Union[str, IOBase, MidiFile, IO], *, clip: bool = True, max_notes: int = 512):
        super().__init__()
        self.context = context
        self.max_notes = max_notes
        if isinstance(file, MidiFile):
            self._base = file
            self._base.clip = clip
        elif isinstance(file, str):
            self._base = MidiFile(filename=file, clip=clip)
        else:
            self._base = MidiFile(file=file, clip=clip)
    
    @property
    def logger(self):
        return self.context.get_logger(f"{self.__class__.__name__}[{self._base.filename}]")
    
    def convert(self) -> Song:
        bpm, sixteenth_note_default = self._evaluate_notes(self._base)
        tracks = self._midi_tracks(self._base, sixteenth_note_default, max_notes=self.max_notes)
        return Song(id=0, bpm=bpm, name=self._base.filename, tracks=tracks)
    
    def _evaluate_notes(self, midi: MidiFile) -> Tuple[int, int]:
        """evaluate notes to get the note/bpm multiplier"""
        bpm = self._midi_bpm(midi)
        sixteenth_note_default = midi.ticks_per_beat / 4
        
        # define variables
        lowestTime = None
        
        # find the lowest non-zero note time
        # does not account for polyphonic / concurrent note events
        for track in midi.tracks:
            for msg in track:
                if not msg.is_meta and msg.time > 0:
                    if lowestTime is None or lowestTime > msg.time:
                        lowestTime = msg.time
        
        # since 16th notes are the lowest available Pulp audio resolution, adjust song translation accordingly
        if lowestTime > sixteenth_note_default:
            # update BPM and sixteenth note time if lowest note value is an even multiple
            if lowestTime % sixteenth_note_default == 0:
                # slow the BPM to account for the decrease in resolution - this allows more song time
                bpm = round(bpm / (lowestTime / sixteenth_note_default))
                sixteenth_note_default = lowestTime
        elif lowestTime < sixteenth_note_default:
            # update BPM and sixteenth note time if lowest note value is an even multiple
            if sixteenth_note_default % lowestTime == 0:
                # increase the BPM to account for the increase in resolution - will result in less song time
                bpm = round(bpm * (sixteenth_note_default / lowestTime))
                sixteenth_note_default = lowestTime
        
        return bpm, sixteenth_note_default
    
    def _midi_bpm(self, midi_file: MidiFile, default: int = 80) -> int:
        """convert tempo to BPM"""
        # set default BPM just in case
        bpm = default
        for msg in midi_file.tracks[0]:
            if msg.type == "set_tempo":
                bpm = round(tempo2bpm(msg.tempo))
                return bpm
        return bpm
    
    def _midi_tracks(self, midi_file: MidiFile, sixteenth_note_default: int, max_notes: int = 0) -> List[Track]:
        """
        collects track data from MIDI file
        and stores it in a list of MIDI Tracks
        """
        newTrackCollection = []
        for i, track in enumerate(midi_file.tracks):
            if i != 0:
                notes = self._get_notes(track, sixteenth_note_default, max_notes)
                newTrack = Track(i, track.name, notes, len(notes))
                newTrackCollection.append(newTrack)
                self.logger.info("Track {}: {}".format(i, track.name))
        return newTrackCollection
    
    def _get_notes(self, midi_track: MidiTrack, sixteenth_note_default: int, max_notes: int = 0) -> List[Note]:
        """get all the notes from a midi track"""
        convertedMIDINotes = []
        noteCounter = 0
        deltaTime = 0
        lastNote = 0
        lastNoteIndex = 0
        for msg in midi_track:
            
            if 0 < max_notes <= noteCounter:
                # hit the max JSON song length - need to truncate
                self.logger.info("Max song length reached. Truncating song.")
                break
            
            if msg.is_meta:  # capture channel_prefix for delayed start time
                if msg.type == "channel_prefix" and msg.time > 0:
                    restEvents = int(msg.time / sixteenth_note_default)
                    while restEvents != 0:
                        # add empty events for rest positions
                        new_json_note = Note()
                        convertedMIDINotes.append(new_json_note)
                        noteCounter += 1
                        restEvents -= 1
                continue
            
            if msg.type == "note_on":
                # handling polyphony - not supported on playdate
                if lastNote != 0:
                    deltaTime += msg.time
                else:
                    if msg.time != 0:
                        restEvents = int(msg.time / sixteenth_note_default)
                        while restEvents != 0:
                            # add empty events for rest positions
                            new_json_note = Note()
                            convertedMIDINotes.append(new_json_note)
                            noteCounter += 1
                            restEvents -= 1
                    
                    lastNote = msg.note
                    deltaTime = 0
                    noteValue = self._note_value(msg.note)
                    noteOctave = self._note_octave(msg.note)
                    noteLen = 1
                    new_json_note = Note(noteValue, noteOctave, noteLen)
                    convertedMIDINotes.append(new_json_note)
                    lastNoteIndex = noteCounter
                    noteCounter += 1
            
            elif msg.type == "note_off" and lastNote == msg.note:
                lastNote = 0
                deltaTime += msg.time
                
                noteLen = self._note_length(deltaTime, sixteenth_note_default)
                convertedMIDINotes[lastNoteIndex].length = noteLen
                
                if deltaTime / sixteenth_note_default >= 2:
                    # add empty events for sustained note durations
                    restEvents = int(deltaTime / sixteenth_note_default)
                    restEvents -= 1  # accounts for note data already stored above
                    
                    while restEvents != 0:
                        # add empty events for rest positions
                        new_json_note = Note()
                        convertedMIDINotes.append(new_json_note)
                        noteCounter += 1
                        restEvents -= 1
        
        return convertedMIDINotes
    
    def _note_value(self, note_int: int) -> int:
        """converts MIDI note to JSON note value"""
        noteValue = note_int % 12  # 12 note scale
        return noteValue + 1  # JSON format is a 1-based index
    
    def _note_octave(self, note_int: int) -> int:
        """gets the JSON note octave from MIDI note value"""
        if note_int >= 24:
            noteOctave = int(note_int / 12)  # divide by 12 and round down
            noteOctave -= 2
        else:
            noteOctave = 0  # anything below octave 0 is set to 0
        return noteOctave
    
    def _note_length(self, note_time: int, sixteenth_note_default: int) -> int:
        """gets JSON note length (in 16ths) from MIDI note time"""
        if note_time < sixteenth_note_default:
            noteLen = 1
        else:
            noteLen = int(note_time / sixteenth_note_default)
        return noteLen
