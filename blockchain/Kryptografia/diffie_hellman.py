print("Diffie-Hellman klasycznie")

# klasyczny DH – tylko demonstracja
p = 127
g = 11

# Alice
a = 123
A = pow(g, a, p)  # 5^6 mod 23
print("Alice publ:", A)

# Bob
b = 152
B = pow(g, b, p)  # 5^15 mod 23
print("Bob publ:", B)

# Wymiana i obliczenie sekretu
s_alice = pow(B, a, p)
s_bob = pow(A, b, p)

print("Sekret Alice:", s_alice)
print("Sekret Bob:  ", s_bob)


from bitcoin_field import G, PrivateKey
from hashlib import sha256
from random import randint

print("Diffie-Hellman na ECC")

# Alice
a = randint(1, 2**256)
alice_priv = PrivateKey(secret=a)
alice_pub = alice_priv.point
print("Alice publ:", alice_pub)

# Bob
b = randint(1, 2**256)
bob_priv = PrivateKey(secret=b)
bob_pub = bob_priv.point
print("Bob publ:", bob_pub)

# Wspólny sekret: punkt na krzywej
alice_shared = a * bob_pub
bob_shared = b * alice_pub

print("\nWspólny punkt Alice:", alice_shared)
print("Wspólny punkt Bob:  ", bob_shared)
print("Czy równe?         ", alice_shared == bob_shared)

# Wyprowadź klucz symetryczny (np. do AES)
shared_secret = alice_shared.x.num.to_bytes(32, 'big')
key = sha256(shared_secret).digest()
print("\nWspólny klucz (SHA256):", key.hex())

