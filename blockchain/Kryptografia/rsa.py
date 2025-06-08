from random import randint
from hashlib import sha256
from math import gcd

# --- narzędzia matematyczne ---

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0:
            return False
    return True

def modinv(a, m):
    # rozszerzony algorytm Euklidesa
    lm, hm = 1, 0
    low, high = a % m, m
    while low > 1:
        r = high // low
        nm, new = hm - lm * r, high - low * r
        lm, low, hm, high = nm, new, lm, low
    return lm % m

def generate_prime(bits=8):
    while True:
        p = randint(2**(bits-1), 2**bits - 1)
        if is_prime(p):
            return p

# --- Klucze RSA ---

class RSAKeyPair:
    def __init__(self, bits=8):
        self.p = generate_prime(bits)
        self.q = generate_prime(bits)
        while self.q == self.p:  
            self.q = generate_prime(bits)
        self.n = self.p * self.q
        self.phi = (self.p - 1) * (self.q - 1)

        # Wybierz e takie, że 1 < e < phi i gcd(e, phi) = 1
        self.e = 3
        while gcd(self.e, self.phi) != 1:
            self.e += 2

        self.d = modinv(self.e, self.phi)

    def public_key(self):
        return (self.e, self.n)

    def private_key(self):
        return (self.d, self.n)

# --- Szyfrowanie i deszyfrowanie ---

def rsa_encrypt(msg: int, pubkey):
    e, n = pubkey
    return pow(msg, e, n)

def rsa_decrypt(cipher: int, privkey):
    d, n = privkey
    return pow(cipher, d, n)

def rsa_sign(msg: int, privkey):
    d, n = privkey
    return pow(msg, d, n)

def rsa_verify(msg: int, signature: int, pubkey):
    e, n = pubkey
    return pow(signature, e, n) == msg


# --- Demo ---

def main():
    print("RSA demo (bez bibliotek)")

    # 8-bitowe liczby – tylko demonstracja
    rsa = RSAKeyPair(bits=8)

    print(f"p = {rsa.p}, q = {rsa.q}")
    print(f"n = {rsa.n}, phi = {rsa.phi}")
    print(f"e = {rsa.e}, d = {rsa.d}")

    pub = rsa.public_key()
    priv = rsa.private_key()

    # Wiadomość jako liczba
    message = 42
    print(f"\nWiadomość: {message}")

    cipher = rsa_encrypt(message, pub)
    print(f"Zaszyfrowana: {cipher}")

    plain = rsa_decrypt(cipher, priv)
    print(f"Odszyfrowana: {plain}")

    # --- podpis RSA ---
    signature = rsa_sign(message, priv)
    print(f"\nPodpis: {signature}")

    ok = rsa_verify(message, signature, pub)
    print(f"Czy podpis poprawny? {ok}")

    # Weryfikacja dla innej wiadomości
    bad = rsa_verify(message + 1, signature, pub)
    print(f"Czy podpis działa dla innej wiadomości? {bad}")



if __name__ == "__main__":
    main()
