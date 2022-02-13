import os
from logging import Logger
from typing import List, Tuple, Any
from json import JSONEncoder
from dataclasses import is_dataclass, asdict

from mido.midifiles.midifiles import MidiFile
from mido.midifiles.tracks import MidiTrack
from mido.midifiles.units import tempo2bpm

from playdate_midi_converter.config import Context
from playdate_midi_converter.JSON_Elements import JSON_Songs, JSON_Notes
from playdate_midi_converter.MIDI_Elements import MIDI_Track
from playdate_midi_converter.ui.input import choose
from playdate_midi_converter.song import Song, Note


class JsonEncodable(object):
    @property
    def json_default(self):
        if is_dataclass(self):
            # noinspection PyDataclass
            return asdict(self)
        raise NotImplementedError()


class ConversionError(Exception):
    pass


class Converter(object):
    context: Context
    
    def __init__(self, context: Context):
        super().__init__()
        self.context = context
    
    @property
    def log(self) -> Logger:
        return self.context.get_logger(self.__class__.__name__)
    
    def convert(self, midi_file: MidiFile) -> JSON_Songs:
        self.log.info("Selected MIDI Filename: " + midi_file.filename)
        
        # get bpm and clock info
        songBPM = self.get_midi_bpm(midi_file)
        ticksPerBeat = midi_file.ticks_per_beat
        sixteenthNoteDefault = ticksPerBeat / 4
        
        self.log.info("MIDI Ticks per beat: " + str(midi_file.ticks_per_beat))
        self.log.info("MIDI BPM: " + str(songBPM))
        
        # capture all tracks
        midiTracks = self.get_tracks(midi_file)
        
        # TODO: Join MIDI Tracks by Instrument (e.g. to handle Logic Regions on Export)
        
        # evaluate tracks to get lowest note value (1/16, 1/32 or 1/64)
        
        songBPM, sixteenthNoteDefault = self.get_note_multiplier(midi_file, songBPM, sixteenthNoteDefault)
        
        # assign pulp synth channels
        tracksAssigned = self.get_track_mapping(midiTracks)
        
        # exit if the user did not assign any tracks
        if not tracksAssigned:
            raise ConversionError("No tracks assigned. Exiting application.")
        
        # create new song if the user has assigned track maps
        songName = input("Enter your song's name:")
        userSong = JSON_Songs(0, songBPM, songName)
        
        # evaluate notes for each track and assign to song
        for track in midiTracks:
            print(str(track.track_number) + " - " + track.track_name + " is mapped to " + track.synth_channel)
            notes, ticks = self.get_notes(track.midi_data, sixteenthNoteDefault)
            userSong.set_notes(track.synth_channel, notes)
            userSong.update_ticks(ticks)
        return userSong

    def get_note_multiplier(self, midi_file: MidiFile, bpm: int, sixteenth_note_default: int) -> Tuple[int, int]:
        """evaluate notes to get the note/bpm multiplier"""
        
        # define variables
        lowestTime = None
        
        # find the lowest non-zero note time
        # does not account for polyphonic / concurrent note events
        for track in midi_file.tracks:
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

    def get_midi_bpm(self, midi_file: MidiFile) -> int:
        """convert tempo to BPM"""
        
        # set default BPM just in case
        bpm = 80
        
        for msg in midi_file.tracks[0]:
            if msg.type == "set_tempo":
                bpm = round(tempo2bpm(msg.tempo))
                return bpm
        
        return bpm

    def write_json_file(self, input_file: str, json_song: JSON_Songs):
        """
        write user song data into JSON format
        save file in input MIDI file directory
        """
        
        outputFile = os.path.splitext(input_file)[0]
        outputFile = outputFile + ".json"
        fileCopyCount = 1
        
        while os.path.exists(outputFile):
            outputFile = os.path.splitext(input_file)[0]
            outputFile = outputFile + "_" + str(fileCopyCount) + ".json"
            fileCopyCount += 1
        
        f = open(outputFile, "a")
        
        # write pre-note content
        outputString = (
            ",".join((
                '[{"id":' + str(json_song.id),
                '"bpm":' + str(json_song.bpm),
                '"name":"' + json_song.name + '"',
                '"notes":'
            ))
        )
        
        f.write(outputString)
        
        # write note content
        outputString = self.write_json_notes(json_song)
        
        f.write(outputString)
        
        # write post-note content
        outputString = (
            ",".join((
                '"ticks":' + str(json_song.ticks),
                '"splits":' + json_song.splits,
                '"loopFrom":' + str(json_song.loop_from)
            ))
        )
        
        outputString = outputString + "}]"
        
        f.write(outputString)
        
        f.close()
        
        print("JSON file written and saved to " + outputFile)

    def write_json_notes(self, json_song: JSON_Songs) -> str:
        """
        capture notes from the JSON_Songs object
        and write to text string for output
        """
        
        noteString = "[["
        
        if json_song.sineNotes is not None:
            for i, note in enumerate(json_song.sineNotes):
                if i == 0:
                    noteString = noteString + ",".join((str(note.value), str(note.octave), str(note.length)))
                else:
                    noteString = ",".join((noteString, str(note.value), str(note.octave), str(note.length)))
        
        noteString = noteString + "],["
        
        if json_song.squareNotes is not None:
            for i, note in enumerate(json_song.squareNotes):
                if i == 0:
                    noteString = noteString + ",".join((str(note.value), str(note.octave), str(note.length)))
                else:
                    noteString = ",".join((noteString, str(note.value), str(note.octave), str(note.length)))
        
        noteString = noteString + "],["
        
        if json_song.sawNotes is not None:
            for i, note in enumerate(json_song.sawNotes):
                if i == 0:
                    noteString = noteString + ",".join((str(note.value), str(note.octave), str(note.length)))
                else:
                    noteString = ",".join((noteString, str(note.value), str(note.octave), str(note.length)))
        
        noteString = noteString + "],["
        
        if json_song.triNotes is not None:
            for i, note in enumerate(json_song.triNotes):
                if i == 0:
                    noteString = noteString + ",".join((str(note.value), str(note.octave), str(note.length)))
                else:
                    noteString = ",".join((noteString, str(note.value), str(note.octave), str(note.length)))
        
        noteString = noteString + "],["
        
        if json_song.noiseNotes is not None:
            for i, note in enumerate(json_song.noiseNotes):
                if i == 0:
                    noteString = noteString + ",".join((str(note.value), str(note.octave), str(note.length)))
                else:
                    noteString = ",".join((noteString, str(note.value), str(note.octave), str(note.length)))
        
        noteString = noteString + "]],"
        
        return noteString

    def get_notes(self, midi_track: MidiTrack, sixteenth_note_default: int) -> Tuple[List[JSON_Notes], int]:
        """get all the notes from a midi track and store in a JSON_Notes object"""
        
        convertedMIDINotes = []
        noteCounter = 0
        deltaTime = 0
        lastNote = 0
        lastNoteIndex = 0
        
        for msg in midi_track:
            
            if noteCounter == 512:
                # hit the max JSON song length - need to truncate
                self.log.info("Max song length reached. Truncating song.")
                break
            
            if msg.is_meta:  # capture channel_prefix for delayed start time
                if msg.type == "channel_prefix" and msg.time > 0:
                    restEvents = int(msg.time / sixteenth_note_default)
                    while restEvents != 0:
                        # add empty events for rest positions
                        new_json_note = JSON_Notes()
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
                            new_json_note = JSON_Notes()
                            convertedMIDINotes.append(new_json_note)
                            noteCounter += 1
                            restEvents -= 1
                    
                    lastNote = msg.note
                    deltaTime = 0
                    noteValue = self.get_note_value(msg.note)
                    noteOctave = self.get_note_octave(msg.note)
                    noteLen = 1
                    new_json_note = JSON_Notes(noteValue, noteOctave, noteLen)
                    convertedMIDINotes.append(new_json_note)
                    lastNoteIndex = noteCounter
                    noteCounter += 1
                
            elif msg.type == "note_off" and lastNote == msg.note:
                lastNote = 0
                deltaTime += msg.time
                
                noteLen = self.get_note_length(deltaTime, sixteenth_note_default)
                convertedMIDINotes[lastNoteIndex].length = noteLen
                
                if deltaTime / sixteenth_note_default >= 2:
                    # add empty events for sustained note durations
                    restEvents = int(deltaTime / sixteenth_note_default)
                    restEvents -= 1  # accounts for note data already stored above
                    
                    while restEvents != 0:
                        # add empty events for rest positions
                        new_json_note = JSON_Notes()
                        convertedMIDINotes.append(new_json_note)
                        noteCounter += 1
                        restEvents -= 1
        
        return convertedMIDINotes, noteCounter

    def get_note_value(self, note_int: int) -> int:
        """converts MIDI note to JSON note value"""
        
        noteValue = note_int % 12  # 12 note scale
        noteValue += 1  # JSON format is a 1-based index
        
        return noteValue

    def get_note_octave(self, note_int: int) -> int:
        """gets the JSON note octave from MIDI note value"""
        
        if note_int >= 24:
            noteOctave = int(note_int / 12)  # divide by 12 and round down
            noteOctave -= 2
        else:
            noteOctave = 0  # anything below octave 0 is set to 0
        
        return noteOctave

    def get_note_length(self, note_time: int, sixteenth_note_default: int) -> int:
        """gets JSON note length (in 16ths) from MIDI note time"""
        
        if note_time < sixteenth_note_default:
            noteLen = 1
        else:
            noteLen = int(note_time / sixteenth_note_default)
        
        return noteLen

    def get_tracks(self, midi_file: MidiFile) -> List[MIDI_Track]:
        """
        collects track data from MIDI file
        and stores it in a list of MIDI Tracks
        """
        
        newTrackCollection = []
        
        for i, track in enumerate(midi_file.tracks):
            if i != 0:
                newTrack = MIDI_Track(i, track, track.name)
                newTrackCollection.append(newTrack)
                self.log.info("Track {}: {}".format(i, track.name))
        
        return newTrackCollection

    def get_track_mapping(self, midi_tracks: List[MIDI_Track]) -> bool:
        """
        use "pick" to collect MIDI track mapping
        to Pulp synth channels from the user via Terminal
        """
        
        trackValidator = False
        availableSynthList = self.context.config['synth']['channels']
        trackNumber = 0
        print("You must map each MIDI track to one of Pulp's 5 synth engines.")
        while trackNumber < len(midi_tracks):
            mappingPrompt = "Please select an engine for " + midi_tracks[trackNumber].track_name
            synthOptions = availableSynthList
            selectedSynth, selectedIndex = choose(self.context, synthOptions, mappingPrompt)
            
            self.log.info(
                f"User selected {selectedSynth} for Track {str(midi_tracks[trackNumber].track_number)} - {midi_tracks[trackNumber].track_name}")
            
            if selectedSynth != "Ignore Track":
                trackValidator = True
                midi_tracks[trackNumber].synth_channel = selectedSynth
                synthOptions.remove(selectedSynth)
            
            trackNumber += 1
        
        return trackValidator


class SongJsonEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Song):
            return self.encode_song(o)
        if isinstance(o, Note):
            return self.encode_note(o)
        return super().default(o)
    
    def encode_song(self, song: Song):
        return {
            'id': song.id,
            'bpm': song.bpm,
            'name': song.name,
            'notes': map(lambda t: t.notes, song.tracks),
            'ticks': str(song.ticks),
            'splits': [[], [], [], [], []],
            'loopFrom': str(song.loop_from),
        }
    
    def encode_note(self, note: Note):
        return [note.value, note.octave, note.length]
