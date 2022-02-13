from typing import Union, Dict, List, Iterable

from playdate_midi_converter.JSON_Elements.JSON_Notes import JSON_Notes


class JSON_Songs():
    # This class scores all the requisite song info
    # At completion, will be joined and exported as a single line
    # in the final .json output file
    
    # setting the "Loop From" value as a constant
    loopFrom = 0
    # setting the splits as a null constant - may add support later
    splits = '[[],[],[],[],[]]'
    
    def __init__(self, id_: int, bpm: int, name: str):
        self.id = id_
        self.bpm = bpm
        self.name = name
        self.sineNotes = None
        self.squareNotes = None
        self.sawNotes = None
        self.triNotes = None
        self.noiseNotes = None
        self.ticks = 0

    def _compile_notes(self) -> Iterable[List[int]]:
        return map(lambda n: n.compile(), [
            self.sineNotes,
            self.squareNotes,
            self.sawNotes,
            self.triNotes,
            self.noiseNotes,
        ])
    
    def set_notes(self, channel: str, notes: List[JSON_Notes]):
        if channel == "Sine":
            self.sineNotes = notes
        elif channel == "Square":
            self.squareNotes = notes
        elif channel == "Sawtooth":
            self.sawNotes = notes
        elif channel == "Triangle":
            self.triNotes = notes
        elif channel == "Noise":
            self.noiseNotes = notes
        else:
            raise ValueError(f"Unexpected synth channel: {channel}")
    
    def update_ticks(self, ticks: int):
        self.ticks = max(self.ticks, ticks)
    
    def compile(self) -> Union[List, Dict]:
        return [{
            'id': self.id,
            'bpm': self.bpm,
            'name': self.name,
            'notes': self._compile_notes(),
            'ticks': str(self.ticks),
            'splits': [[], [], [], [], []],
            'loopFrom': str(self.loopFrom),
        }]
