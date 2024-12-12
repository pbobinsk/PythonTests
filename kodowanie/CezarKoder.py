from Koder import Koder

class CezarKoder(Koder):

    def __init__(self):
        print("Inicjacja Kodera Cezara z domyślnym kluczem 3")
        self.__init__(3)
        

    def __init__(self,klucz):
        print("Inicjacja Kodera Cezara z kluczem "+str(klucz))
        alfabet = ''.join(chr(c) for c in range(ord('A'),ord('Z')+1))
        self.slownik = {k:alfabet[(ord(k)-ord('A')+klucz)%len(alfabet)] for k in alfabet}
        self.invertDict()
        
    # gdy chcemy ograniczyć się do liter, _ separuje wyrazy
    def encode(self,tekstJawny):
        return ''.join(self.slownik[l] if l in self.slownik.keys() else '_' for l in tekstJawny)


    # gdy chcemy ograniczyć się do liter, _ separuje wyrazy
    def decode(self,tekstTajny):
        return ''.join(self.odwrotnySlownik[w] if w in self.odwrotnySlownik.keys() else ' ' for w in tekstTajny)

