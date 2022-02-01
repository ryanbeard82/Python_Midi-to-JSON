# General JSON & MIDI file format notes:
```
[{
    "id":[SONG ID NUMBER - 0 based index],
    "bpm":[bpm integer]
    "name":["name of song as string"]
    "notes:
    [[(sine track notes)],
    [(square track notes)],
    [(sawtooth track notes)],
    [(triangle track notes)],
    [(noise track notes)],
    ]
    "ticks":[number of 1/6th notes in length of the total track],
    "splits": [[sine split locations, in 16'th notes],[square],[sawtooth],[triangle],[noise]],
    "voices":[optional - voice adjustments]
    "loopFrom": [optional loop starting position]
}]
```

### Each note receives 3 values  
    1. The note value on a 12 note linear scale (e.g. 1 = C, 12 = B)  
    2. The octave (0 through 8)  
    3. The duration as the - number of 16th notes  
    
Empty 1/16 note positions are reported as **0,0,0**

**512** total positions available (number of 16'th slots)

Sample MIDI track data:
```
for msg in yourMidiFile.tracks[4]: print(msg.dict())  
{'type': 'channel_prefix', 'channel': 0, 'time': 0}  
{'type': 'track_name', 'name': 'Rhythm - Snare', 'time': 0}  
{'type': 'instrument_name', 'name': 'Rhythm - Snare', 'time': 0}  
{'type': 'note_on', 'time': 0, 'note': 41, 'velocity': 100, 'channel': 0}  
{'type': 'note_on', 'time': 0, 'note': 46, 'velocity': 100, 'channel': 0}  
{'type': 'note_off', 'time': 120, 'note': 41, 'velocity': 64, 'channel': 0}  
{'type': 'note_off', 'time': 0, 'note': 46, 'velocity': 64, 'channel': 0}  
{'type': 'note_on', 'time': 120, 'note': 38, 'velocity': 100, 'channel': 0}  
{'type': 'note_off', 'time': 120, 'note': 38, 'velocity': 64, 'channel': 0}  
{'type': 'note_on', 'time': 120, 'note': 41, 'velocity': 100, 'channel': 0}  
{'type': 'note_off', 'time': 120, 'note': 41, 'velocity': 64, 'channel': 0}  
```