class Koder():
    
    # dla metod słownikowych
    slownik = {}
    odwrotnySlownik = {}

    # dla metod słownikowych
    def invertDict(self):
        self.odwrotnySlownik = {k:v for (v,k) in self.slownik.items()}

    # dla słowników zawierających wyrazy, jak np. dla Morse'a, _ separuje wyrazy, spacja znaki
    def encode(self,tekstJawny):
        return ''.join(self.slownik[l]+' ' if l in self.slownik.keys() else '_' for l in tekstJawny)

    # dla słowników zawierających wyrazy, jak np. dla Morse'a, _ separuje wyrazy, spacja znaki
    def decode(self,tekstTajny):
        return ''.join(self.odwrotnySlownik[w] if w in self.odwrotnySlownik.keys() else ' ' for w in tekstTajny.replace('_',' ').split(' '))

