import hashlib
import random

# Symulowany blok znaleziony przez górnika
mined_block = {
    "previous_block_hash": "000000abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234",
    "transactions": [
        "Alice -> Bob: 1 BTC",
        "Charlie -> Dave: 0.5 BTC",
        "Eve -> Frank: 0.8 BTC"
    ],
    "nonce": 18747094,  # Nonce znalezione przez górnika
    "block_hash": "000000b4a6710792d834d1e9ed9d987157e17d0e0d00c1344d00ca0be63d1d5e"
}

# Funkcja do obliczenia root Merkle
def merkle_root(transactions):
    tx_hashes = [hashlib.sha256(tx.encode()).hexdigest() for tx in transactions]
    while len(tx_hashes) > 1:
        if len(tx_hashes) % 2 == 1:
            tx_hashes.append(tx_hashes[-1])  # Jeśli liczba hashy jest nieparzysta, duplikujemy ostatni
        tx_hashes = [hashlib.sha256((tx_hashes[i] + tx_hashes[i + 1]).encode()).hexdigest()
                     for i in range(0, len(tx_hashes), 2)]
    return tx_hashes[0] if tx_hashes else None

# Funkcja sprawdzająca poprawność bloku (używana przez każdy węzeł)
def verify_block(node_id, block):
    expected_merkle_root = merkle_root(block["transactions"])
    
    # Tworzymy nagłówek bloku
    block_header = f"{block['previous_block_hash']}{expected_merkle_root}{block['nonce']}"
    
    # Obliczamy SHA-256 nagłówka
    calculated_hash = hashlib.sha256(block_header.encode()).hexdigest()
    
    # Sprawdzamy poprawność hash’a i trudność (musi zaczynać się od "0000")
    if calculated_hash == block["block_hash"] and calculated_hash.startswith("0000"):
        print(f"✅ Węzeł {node_id}: Blok jest poprawny!")
        return True
    else:
        print(f"❌ Węzeł {node_id}: Blok jest niepoprawny!")
        return False

# Tworzymy symulowane węzły
num_nodes = 5  # Liczba węzłów w sieci
nodes = [f"Węzeł-{i}" for i in range(1, num_nodes + 1)]

# Każdy węzeł sprawdza poprawność bloku
valid_nodes = []
for node in nodes:
    if verify_block(node, mined_block):
        valid_nodes.append(node)

# Propagacja bloku do innych węzłów, jeśli jest poprawny
if valid_nodes:
    print(f"\n🚀 Blok zostaje zaakceptowany i propagowany przez {len(valid_nodes)} węzłów!")
else:
    print("\n❌ Blok jest odrzucony przez całą sieć!")
