class JSON_Songs():
    # This class scores all the requisite song info
    # At completion, will be joined and exported as a single line
    # in the final .json output file
    
    # setting the "Loop From" value as a constant
    loopFrom = 0
    # setting the splits as a null constant - may add support later
    splits = '[[],[],[],[],[]]'
    
    def __init__ (self, id, bpm, name):
        self.id = id
        self.bpm = bpm
        self.name = name
        self.sineNotes = []
        self.squareNotes = []
        self.sawNotes = []
        self.triNotes = []
        self.noiseNotes = []
        self.ticks = None