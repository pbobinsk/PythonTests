import hashlib
import random

# Funkcja obliczająca hash bloku (symulacja kopania)
def mine_block(previous_hash, transactions, nonce_target="0000"):
    nonce = 0
    merkle_root = hashlib.sha256("".join(transactions).encode()).hexdigest()
    
    while True:
        block_header = f"{previous_hash}{merkle_root}{nonce}"
        block_hash = hashlib.sha256(block_header.encode()).hexdigest()
        
        if block_hash.startswith(nonce_target):
            return {"hash": block_hash, "previous": previous_hash, "transactions": transactions, "nonce": nonce}
        
        nonce += 1

def get_chain_length(block, blockchain):
    length = 0
    current_block = block
    
    while current_block is not None:
        length += 1
        current_block = blockchain.get(current_block["previous"])  # Przechodzimy do poprzedniego bloku

    return length


# Tworzymy pierwszy blok (Genesis Block)
genesis_block = {"hash": "0000000000000000", "previous": None, "transactions": ["Genesis Block"], "nonce": 0}

# Symulujemy kopanie dwóch równoległych bloków po Genesis Block (Fork)
block_A = mine_block(genesis_block["hash"], ["Alice -> Bob: 1 BTC"])
block_B = mine_block(genesis_block["hash"], ["Charlie -> Dave: 0.5 BTC"])

print("\n⛏️  Powstał fork! Dwa górniki wykopali różne bloki:")
print(f"🔷 Blok A: {block_A['hash']} (na podstawie Genesis)")
print(f"🔶 Blok B: {block_B['hash']} (na podstawie Genesis)")

# Sieć podzielona – część węzłów kontynuuje kopanie na Bloku A, część na Bloku B
block_A1 = mine_block(block_A["hash"], ["Eve -> Frank: 0.8 BTC"])
block_B1 = mine_block(block_B["hash"], ["George -> Henry: 2 BTC"])
block_B2 = mine_block(block_B1["hash"], ["Ivan -> Jake: 3 BTC"])  # Blok B1 zyskuje dodatkowy blok!

# Sprawdzamy, który łańcuch jest dłuższy
# chain_A_length = 2  # Genesis -> A -> A1
# chain_B_length = 3  # Genesis -> B -> B1 -> B2

# Tworzymy mapę blockchaina (symulacja struktury przechowującej bloki)
blockchain = {
    genesis_block["hash"]: genesis_block,
    block_A["hash"]: block_A,
    block_A1["hash"]: block_A1,
    block_B["hash"]: block_B,
    block_B1["hash"]: block_B1,
    block_B2["hash"]: block_B2,
}

# Obliczamy długość każdego łańcucha
chain_A_length = get_chain_length(block_A1, blockchain)
chain_B_length = get_chain_length(block_B2, blockchain)

print("\n🔗 Rozwiązanie konfliktu:")
if chain_B_length > chain_A_length:
    print("✅ Sieć wybiera łańcuch B, bo jest dłuższy!")
    print(f"Najdłuższy łańcuch kończy się na bloku: {block_B2['hash']}")
else:
    print("✅ Sieć wybiera łańcuch A, bo jest dłuższy!")
    print(f"Najdłuższy łańcuch kończy się na bloku: {block_A1['hash']}")

print("\n❌ Krótszy łańcuch zostaje odrzucony, transakcje mogą trafić do kolejnych bloków!")

# import networkx as nx
# import matplotlib.pyplot as plt

# def visualize_blockchain(blockchain):
#     G = nx.DiGraph()  # Tworzymy graf skierowany

#     # Dodajemy węzły i krawędzie
#     for block_hash, block in blockchain.items():
#         G.add_node(block_hash[:6])  # Skracamy hash dla lepszej widoczności
#         if block["previous"]:
#             G.add_edge(block["previous"][:6], block_hash[:6])  # Połączenie z poprzednim blokiem

#     # Rysowanie grafu
#     plt.figure(figsize=(8, 5))
#     pos = nx.spring_layout(G, seed=42)  # Automatyczne rozmieszczenie węzłów
#     nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray", node_size=2000, font_size=10, font_weight="bold")
    
#     plt.title("Wizualizacja Blockchaina")
#     plt.show()

# # 🔹 Wywołanie funkcji z przykładowymi danymi
# visualize_blockchain(blockchain)

import matplotlib
matplotlib.use("Agg")  # Używa backendu bez GUI (bez Tcl/Tk)

import networkx as nx
import matplotlib.pyplot as plt

def visualize_blockchain(blockchain):
    G = nx.DiGraph()  # Graf skierowany

    # Dodajemy węzły i krawędzie
    for block_hash, block in blockchain.items():
        G.add_node(block_hash[:6])  # Skrócony hash dla czytelności
        if block["previous"]:
            G.add_edge(block["previous"][:6], block_hash[:6])  # Połączenie do poprzedniego bloku

    # Rysowanie grafu BEZ użycia Tkinter
    plt.figure(figsize=(8, 5))
    pos = nx.spring_layout(G, seed=42)  # Rozkład węzłów
    nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray", node_size=2000, font_size=10, font_weight="bold")

    # Zamiast plt.show(), zapisujemy do pliku
    plt.savefig("blockchain_graph.png")  # Możesz użyć PNG, SVG, PDF itd.
    print("✅ Wygenerowano graf blockchaina jako blockchain_graph.png")


# 🔹 Generujemy wizualizację
visualize_blockchain(blockchain)
