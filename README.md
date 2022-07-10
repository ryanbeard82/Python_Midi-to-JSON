#PlayDate Pulp Midi-to-JSON Converter
*Developed by Ryan Beard and Anthony Beard of [Bro-Code.dev](https://bro-code.dev)

*This simple command line utility to convert standard MIDI (.mid) files into the PlayDate Pulp's JSON (.json) audio schema for import into the web-based development environment.*

##The PlayDate Pulp's JSON Audio Format Spec

The Pulp's audio spec (*below*) follows a simple comma delimited schema that allows the import of multilple song contents within a single file.
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
Each song contains four sections that itentify the *id, bpm, name,* and *notes*.

- *ID*: The 0-based index of the song within the collection of songs. Allows update of existing songs.
- *BPM*: the songs integer tempo as displayed in the Pulp editor
- *NAME*: The song name to be displayed in Pulp "Songs" dropdown list.
- *NOTES*: The comprehensive list of note events in the song, arranged by track.

Notes are arranged by track in the following sequence:
- Sine Track
- Square Track
- Sawtooth Track
- Traingle Track
- Noise Track

Each track must be present in the import file, even if it contains no notes. Empty tracks are presented as an empty list/array: [ ].

Within a track, note are stored as tuples. Each note must contain the following:
- The note value, represented as an integer on a 12 note linear scale (*1 = C, 12 = B*)
- The note octave (*0 through 8*)
- The duration of the note in number of 1/16th note increments (*e.g. an 1/8 note would be **2***)

Rests are stored as empty 1/6th note tuplets (*e.g. 0,0,0*). **This includes empty 1/6th note positions that occur under other sustained notes.** For example, an 1/8th note would be represented with two tuples: one for the note start event during the first 1/16th note, and one for the sustained note held during the second 1/16th note.
**<p align="center">[<span style="color:blue">1,1,2,</span><span style="color:green">0,0,0</span>]**</p>

There are a total of **512** note positions available (*1/16th note slots*) in each pulp song.

##Installing the PlayDate MIDI Converter

To install the PlayDate Midi Converter, run the following command:

    pip install playdate-midi-converter

Note that the PlayDate MIDI Converter requires **Python 3.9.\*** or higher.

During installation, the following dependencies will also be installed:
- mido v1.2.10
- pathlib v1.0.1
- pick v1.2.0
##Running the Audio Converter
Run the PlayDate MIDI Converter with the following command:

    playdate-pulp-midi

You can specifcy a .mid input and .json output file with the ```-i``` and ```-o``` arguments, but if none are applied, you will be prompted to select an input file and save location with your operating systems native file explorer.

For each track present in the input MIDI file, you will be required to map it to one of the 5 avialable PlayDate Pulp audio tracks, or you can choose to ignore the midi track.
```
Please assign track #1 "Inst 1" to a channel:
        [0]     (Ignore)
        [1]     Sine
        [2]     Square
        [3]     Sawtooth
        [4]     Triangle
        [5]     Noise
```
Each PlayDate Pulp audio track can only be assigned once. After each track has been assigned, and the mappings have been, the .json output file is saved to the user specific location.

**Conversion Notes**

Note that during the conversion, the MIDI file is evaluated for track tempo and minimum note denomomination. This allows the resulting JSON file to be scaled to maximize the usage of the available **512** note positions. For example, if an input MIDI file has no notes shorter than a 1/4 note, the tempo can be divided by 4 and the 1/4 notes can be represented as 1/6th notes to allow more note content in the ouput file.