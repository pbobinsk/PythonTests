import hashlib

def calculate_sha256(data_string): # Już zdefiniowana wcześniej
    return hashlib.sha256(data_string.encode('utf-8')).hexdigest()

transactions = [
    "Alicja wysyła 1 BTC do Boba",
    "Bob wysyła 0.5 BTC do Karoliny",
    "Dawid wysyła 2 BTC do Ewy",
    "Filip wysyła 0.1 BTC do Grzegorza"
]

# 1. Hashujemy poszczególne transakcje (liście)
tx_hashes = [calculate_sha256(tx) for tx in transactions]
print("Hashe transakcji (liście):")
for i, h in enumerate(tx_hashes):
    print(f"  TX{i+1}: {h}")

if len(tx_hashes) % 2 != 0: # Jeśli nieparzysta liczba, duplikujemy ostatni
    tx_hashes.append(tx_hashes[-1])

# 2. Łączymy hashe parami i hashujemy (pierwszy poziom wewnętrzny)
level1_hashes = []
for i in range(0, len(tx_hashes), 2):
    combined_hash_input = tx_hashes[i] + tx_hashes[i+1]
    level1_hashes.append(calculate_sha256(combined_hash_input))

print("\nHashe poziomu 1:")
for i, h in enumerate(level1_hashes):
    print(f"  H({i*2+1},{i*2+2}): {h}")

# 3. Jeśli mamy więcej niż jeden hash, powtarzamy, aż dojdziemy do korzenia
# W tym przypadku dla 4 transakcji, mamy 2 hashe na poziomie 1
if len(level1_hashes) == 1:
    merkle_root = level1_hashes[0]
else: # Dla >2 haszy na poziomie 1 (np. 8 transakcji początkowych)
    if len(level1_hashes) % 2 != 0:
         level1_hashes.append(level1_hashes[-1])
    
    merkle_root_input = level1_hashes[0] + level1_hashes[1] # Dla 4 transakcji
    # Dla więcej, potrzebna by była pętla
    merkle_root = calculate_sha256(merkle_root_input)

print(f"\nKorzeń Merkle'a (Merkle Root): {merkle_root}")