from simple_block import Block
import hashlib
import time

# (kontynuacja poprzedniego kodu z klasą Block)
blockchain = []

def create_genesis_block():
    # Używamy naszej klasy Block
    return Block(0, "0" * 64, time.time(), "Blok Genesis", 0)

def add_new_block(previous_block, data):
    index = previous_block.index + 1
    timestamp = time.time()
    # W prawdziwym blockchainie (np. PoW) znalezienie nonce wymagałoby pracy
    # Tutaj dla uproszczenia, nonce może być stałe lub losowe,
    # bo nie implementujemy jeszcze mechanizmu konsensusu PoW.
    # Na razie przyjmijmy nonce=0 dla prostoty.
    new_block = Block(index, previous_block.hash, timestamp, data, 0)
    return new_block

# Inicjalizacja blockchaina
blockchain.append(create_genesis_block())
print("Stworzono Blok Genesis:")
print(blockchain[0])

# Dodawanie nowych bloków
num_blocks_to_add = 3
for i in range(1, num_blocks_to_add + 1):
    new_data = f"Transakcje w bloku #{i}"
    new_block = add_new_block(blockchain[-1], new_data)
    blockchain.append(new_block)
    print(f"\nDodano blok #{i}:")
    print(blockchain[-1])

# Demonstracja niezmienności (koncepcyjna)
print("\n--- Demonstracja (próba) zmiany danych w bloku ---")
if len(blockchain) > 1:
    block_to_tamper = blockchain[1] # Weźmy pierwszy blok po Genesis
    print(f"Oryginalny hash bloku #{block_to_tamper.index}: {block_to_tamper.hash}")
    original_data = block_to_tamper.data
    block_to_tamper.data = "Sfałszowane dane!"
    # Ważne: w naszym prostym modelu musimy ręcznie przeliczyć hash
    # W prawdziwym blockchainie węzły by to wykryły.
    # Ale jeśli byśmy nie przeliczyli hasha, to dane i hash byłyby niespójne.
    # Jeśli przeliczymy, to hash się zmieni:
    tampered_hash = block_to_tamper.calculate_hash() # Przeliczamy po zmianie
    print(f"Dane zmienione. Nowy (obliczony) hash bloku #{block_to_tamper.index}: {tampered_hash}")

    # Sprawdźmy, czy pasuje do hasha zapisanego w następnym bloku
    if len(blockchain) > 2:
        next_block = blockchain[2]
        print(f"Hash poprzedniego bloku zapisany w bloku #{next_block.index}: {next_block.previous_hash}")
        if next_block.previous_hash == tampered_hash:
            print("BŁĄD KONSEPTUALNY: W naszym modelu nie ma automatycznej walidacji łańcucha.")
            print("Gdybyśmy chcieli, aby zmiana była 'poprawna', musielibyśmy zaktualizować 'previous_hash' w bloku 2,")
            print("a potem przeliczyć hash bloku 2, co zmieniłoby jego hash, co wymusiłoby zmianę w bloku 3 itd.")
        else:
            print("ZAUWAŻ: Zmieniony hash bloku 1 NIE PASUJE do 'previous_hash' w bloku 2.")
            print("Łańcuch jest przerwany!")
    # Przywróćmy dla porządku
    block_to_tamper.data = original_data
    block_to_tamper.hash = block_to_tamper.calculate_hash() # Przywracamy oryginalny hash