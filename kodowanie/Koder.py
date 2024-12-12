class Koder():
    
    # dla metod słownikowych
    slownik = {}
    odwrotnySlownik = {}

    def __init__(self):
        print('Inicjacja Kodera abstrakcyjnego')

    def invertDict(self):
        self.odwrotnySlownik = {k:v for (v,k) in self.slownik.items()}

    def encode(self,tekstJawny):
        print('Słownik do kodowania: '+str(self.slownik))
        return ''.join(self.slownik[l]+' ' if l in self.slownik.keys() else '_' for l in tekstJawny)


    def decode(self,tekstTajny):
        print('Słownik do dekodowania: '+str(self.odwrotnySlownik))
        return ''.join(self.odwrotnySlownik[w] if w in self.odwrotnySlownik.keys() else ' ' for w in tekstTajny.replace('_',' ').split(' '))

