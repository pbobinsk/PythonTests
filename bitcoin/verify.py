import hashlib

# Otrzymany blok (z poprzedniej symulacji)
received_block = {
    "previous_block_hash": "000000abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234",
    "transactions": [
        "Alice -> Bob: 1 BTC",
        "Charlie -> Dave: 0.5 BTC",
        "Eve -> Frank: 0.8 BTC"
    ],
    "nonce": 18747094,  # Nonce znalezione przez górnika
    "block_hash": "000000b4a6710792d834d1e9ed9d987157e17d0e0d00c1344d00ca0be63d1d5e"
}

# Funkcja do obliczenia root Merkle (jak poprzednio)
def merkle_root(transactions):
    tx_hashes = [hashlib.sha256(tx.encode()).hexdigest() for tx in transactions]
    while len(tx_hashes) > 1:
        if len(tx_hashes) % 2 == 1:
            tx_hashes.append(tx_hashes[-1])  # Duplikujemy ostatni hash, jeśli nieparzysta liczba
        tx_hashes = [hashlib.sha256((tx_hashes[i] + tx_hashes[i + 1]).encode()).hexdigest()
                     for i in range(0, len(tx_hashes), 2)]
    return tx_hashes[0] if tx_hashes else None

# Weryfikacja root Merkle
expected_merkle_root = merkle_root(received_block["transactions"])

# Weryfikacja PoW
block_header = f"{received_block['previous_block_hash']}{expected_merkle_root}{received_block['nonce']}"
calculated_hash = hashlib.sha256(block_header.encode()).hexdigest()

# Sprawdzamy, czy hash bloku i root Merkle są poprawne
if calculated_hash == received_block["block_hash"] and received_block["block_hash"].startswith("0000"):
    print("\n✅ Blok jest poprawny! Może zostać dodany do blockchaina.")
else:
    print("\n❌ Błąd! Blok jest nieprawidłowy.")
