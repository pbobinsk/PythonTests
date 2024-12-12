from Koder import Koder

class MorseKoder(Koder):
    slownik = {  
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 
    'E': '.', 'F': '..-.', 'G': '--.', 'H': '....', 
    'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 
    'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 
    'Y': '-.--', 'Z': '--..' 
    }

    def __init__(self):
        print("Inicjacja Kodera Morse'a")
        self.invertDict()

    
