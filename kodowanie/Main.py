from CezarKoder import CezarKoder
from MorseKoder import MorseKoder


print('=== Klasa MorseKoder ===')

koder = MorseKoder()

jawny = 'ALA MA KOTA'
print(jawny)
tajny = koder.encode(jawny)
print(tajny)
jawny = koder.decode(tajny)
print(jawny)

print('=== Klasa CezarKoder ===')

koder = CezarKoder(5)

jawny = 'ALA MA KOTA'
print(jawny)
tajny = koder.encode(jawny)
print(tajny)
jawny = koder.decode(tajny)
print(jawny)
