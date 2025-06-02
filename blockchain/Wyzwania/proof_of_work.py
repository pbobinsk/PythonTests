import hashlib
import time

# Przykładowe uproszczone transakcje
transactions = [
    "Alice -> Bob: 1 BTC",
    "Charlie -> Dave: 0.5 BTC",
    "Eve -> Frank: 0.8 BTC"
]

# Funkcja do obliczenia uproszczonego root Merkle (łączenie hashy)
def merkle_root(transactions):
    tx_hashes = [hashlib.sha256(tx.encode()).hexdigest() for tx in transactions]
    while len(tx_hashes) > 1:
        if len(tx_hashes) % 2 == 1:
            tx_hashes.append(tx_hashes[-1])  # Jeśli liczba hashy jest nieparzysta, duplikujemy ostatni
        tx_hashes = [hashlib.sha256((tx_hashes[i] + tx_hashes[i + 1]).encode()).hexdigest()
                     for i in range(0, len(tx_hashes), 2)]
    return tx_hashes[0] if tx_hashes else None

# Parametry nagłówka bloku
previous_block_hash = "000000abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234"  # Hash poprzedniego bloku
merkle_root_hash = merkle_root(transactions)  # Hash drzewa Merkle
target_prefix = "000000"  # Trudność kopania (hash musi zaczynać się od "0000")

# Kopanie bloku (Proof of Work)
def mining (target_prefix = "0000"):
    nonce = 0
    start_time = time.time()
    while True:
        # Tworzymy zawartość bloku (uproszczona)
        block_header = f"{previous_block_hash}{merkle_root_hash}{nonce}"
        
        # Obliczamy hash bloku
        block_hash = hashlib.sha256(block_header.encode()).hexdigest()
        
        # Sprawdzamy, czy hash spełnia warunek trudności
        if block_hash.startswith(target_prefix):
            end_time = time.time()
            print("\n✅ Znaleziono poprawny blok!")
            print(f"Nonce: {nonce}")
            print(f"Hash bloku: {block_hash}")
            print(f"Czas kopania: {end_time - start_time:.2f} sekundy")
            break  # Kopanie zakończone
        
        # Jeśli nie, zwiększamy nonce i próbujemy dalej
        nonce += 1
    return end_time - start_time

t3 = mining("000")
t4 = mining()
t5 = mining("00000")
t6 = mining("000000")

print(f"{t3:.2f} s, {t4:.2f} s, {t5:.2f} s, {t6:.2f} s")