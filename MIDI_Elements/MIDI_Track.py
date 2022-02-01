class MIDI_Track():
    # This class stores a midi track from the input file
    # It adds additional variables to help track the JSON mapping
    # And includes helper methods for parsing data
    
    def __init__ (self, track_number, midi_data,track_name):
        self.track_number = track_number
        self.midi_data = midi_data
        self.track_name = track_name
        self.synth_channel = None