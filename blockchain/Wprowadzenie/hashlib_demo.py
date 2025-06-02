import hashlib

'''
encode('utf-8') jest potrzebne, bo funkcje hashujące operują na bajtach, 
a nie bezpośrednio na stringach Pythona. 
hexdigest() konwertuje binarny hash na czytelną postać heksadecymalną
'''

def calculate_sha256(data_string):
    return hashlib.sha256(data_string.encode('utf-8')).hexdigest()

text1 = "Witaj świecie blockchain!"
hash1 = calculate_sha256(text1)
print(f"Dane: '{text1}'\nSHA-256: {hash1}\n")

text2 = "Witaj świecie blockchain." # Zmiana jednego znaku (wykrzyknik na kropkę)
hash2 = calculate_sha256(text2)
print(f"Dane: '{text2}'\nSHA-256: {hash2}\n") # Pokaż, jak bardzo się różni

# Pokaż stałą długość hasha
text_short = "a"
hash_short = calculate_sha256(text_short)
print(f"Dane: '{text_short}'\nSHA-256: {hash_short} (Długość: {len(hash_short)})\n")

text_long = "To jest bardzo długi tekst, który zostanie zahashowany przy użyciu SHA-256."
hash_long = calculate_sha256(text_long)
print(f"Dane: '{text_long}'\nSHA-256: {hash_long} (Długość: {len(hash_long)})\n")