import hashlib
import time

class Block:
    def __init__(self, index, previous_hash, timestamp, data, nonce=0):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = str(data) # Dane mogą być np. listą transakcji
        self.nonce = nonce
        # Hash jest obliczany na podstawie wszystkich tych pól
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        # Ważne: kolejność i formatowanie muszą być spójne
        block_content = (str(self.index) +
                         str(self.previous_hash) +
                         str(self.timestamp) +
                         str(self.data) +
                         str(self.nonce))
        return hashlib.sha256(block_content.encode('utf-8')).hexdigest()

    def __str__(self):
        return (f"Block #{self.index}\n"
                f"  Timestamp: {self.timestamp}\n"
                f"  Data: {self.data}\n"
                f"  Nonce: {self.nonce}\n"
                f"  Hash: {self.hash}\n"
                f"  Previous Hash: {self.previous_hash}\n")

# Przykład użycia (na razie bez łańcucha)
genesis_previous_hash = "0" * 64 # Często 64 zera dla pierwszego bloku
block0 = Block(0, genesis_previous_hash, time.time(), "Blok Genesis")
print(block0)
block1 = Block(1, block0.hash, time.time(), "Jakaś transakcja")
print(block1)