from Koder import Koder

class CezarKoder(Koder):

    klucz = 0
    alfabet = ''

    def __init__(self):
        print("Inicjacja Kodera Cezara z domyślnym kluczem 3")
        self.__init__(3)
        

    def __init__(self,klucz):
        print("Inicjacja Kodera Cezara z kluczem "+str(klucz))
        self.alfabet = ''.join(chr(c) for c in range(ord('A'),ord('Z')+1))
        self.slownik = {k:self.alfabet[(ord(k)-ord('A')+klucz)%len(self.alfabet)] for k in self.alfabet}
        self.invertDict()
        self.klucz = klucz
        
    # gdy chcemy ograniczyć się do liter, _ separuje wyrazy
    # def encode(self,tekstJawny):
    #     #return ''.join(self.slownik[l] if l in self.slownik.keys() else '_' for l in tekstJawny)
    #     # albo bez słownika
    #     return ''.join('_' if l not in self.alfabet else chr(ord(l) + self.klucz) if ord(l) + self.klucz <= ord('Z') else chr(ord(l) + self.klucz - ord('Z')) for l in tekstJawny)


    # gdy chcemy ograniczyć się do liter, _ separuje wyrazy
    # def decode(self,tekstTajny):
    #     #return ''.join(self.odwrotnySlownik[w] if w in self.odwrotnySlownik.keys() else ' ' for w in tekstTajny)
    #     # albo bez słownika
    #     return ''.join(' ' if l not in self.alfabet else chr(ord(l) - self.klucz) if ord(l) - self.klucz >= ord('A') else chr(ord(l) - self.klucz + ord('A')) for l in tekstTajny)

