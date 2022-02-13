from dataclasses import dataclass, field
from enum import auto, IntEnum
from typing import Iterable, List, Hashable
from itertools import chain

from playdate_midi_converter.json import JsonEncodable


@dataclass
class Song(JsonEncodable):
    id: int
    bpm: int
    name: str
    tracks: Iterable['Track']
    splits: List[List] = field(default_factory=lambda : [[], [], [], [], []])
    loop_from: int = 0
    
    @property
    def ticks(self) -> int:
        most_ticks = 0
        for t in self.tracks:
            most_ticks = max(most_ticks, t.ticks)
        return most_ticks
    
    def json_default(self):
        return {
            'id': self.id,
            'bpm': self.bpm,
            'name': self.name,
            'notes': list(self.tracks),
            'ticks': self.ticks,
            'splits': self.splits,
            'loopFrom': self.loop_from,
        }


@dataclass
class Track(JsonEncodable, Hashable):
    def __hash__(self) -> int:
        return hash((
            self.number,
            self.name,
        ))

    number: int
    name: str
    notes: Iterable['Note']
    ticks: int = 0
    channel: 'Channel' = None
    
    def json_default(self):
        if self.channel is None:
            return []
        else:
            return list(chain(*map(lambda n: n.json_default(), self.notes)))
    
    def __str__(self):
        return f"{self.number} : {self.name}"


@dataclass
class Note(JsonEncodable):
    value: int = 0
    octave: int = 0
    length: int = 0
    
    def json_default(self):
        return [self.value, self.octave, self.length]


class Channel(IntEnum):
    SINE = auto()
    SQUARE = auto()
    SAWTOOTH = auto()
    TRIANGLE = auto()
    NOISE = auto()
