class JSON_Notes():
    # This class stores the 3 expected JSON note parameters
    #intended to be declared as list variables, one for each wave channel
    
    def __init__ (self,value,octave,length):
        self.value = value
        self.octave = octave
        self.length = length