import hashlib
from random import randint
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Zakładamy, że masz klasy z książki:
from bitcoin_field import PrivateKey, S256Point  # Z książki Jimmy'ego Songa


# Padding do AES-CBC (PKCS#7)
def pad(s):
    padding_len = 16 - len(s) % 16
    return s + bytes([padding_len]) * padding_len

def unpad(s):
    return s[:-s[-1]]


# Funkcja szyfrująca wiadomość (nadawca)
def ecies_encrypt(message: bytes, recipient_pubkey: S256Point):
    # Ephemeral private key (tylko na jedno szyfrowanie)
    ephemeral_priv = PrivateKey(randint(1, 2**256))
    ephemeral_pub = ephemeral_priv.point

    # ECDH – wspólny sekret
    shared_point = ephemeral_priv.secret * recipient_pubkey 
    shared_secret = shared_point.x.num.to_bytes(32, 'big')
    aes_key = hashlib.sha256(shared_secret).digest()

    # Szyfrowanie wiadomości AES-CBC
    iv = get_random_bytes(16)
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(message))

    return {
        'ephemeral_pub': ephemeral_pub,
        'iv': iv,
        'ciphertext': ciphertext
    }


# Funkcja deszyfrująca wiadomość (odbiorca)
def ecies_decrypt(enc_dict, recipient_privkey: PrivateKey):
    ephemeral_pub = enc_dict['ephemeral_pub']
    iv = enc_dict['iv']
    ciphertext = enc_dict['ciphertext']

    # ECDH – ten sam wspólny sekret
    shared_point = recipient_privkey.secret * ephemeral_pub
    shared_secret = shared_point.x.num.to_bytes(32, 'big')
    aes_key = hashlib.sha256(shared_secret).digest()

    # Odszyfrowanie
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    padded_plaintext = cipher.decrypt(ciphertext)
    return unpad(padded_plaintext)


# 🔁 Przykład działania
def main():
    print("Generowanie kluczy ECC")
    # Klucz prywatny odbiorcy
    bob_priv = PrivateKey(randint(1, 2**256))
    bob_pub = bob_priv.point

    # Wiadomość
    msg = b"Tajna wiadomosc dla Boba"

    print("Szyfrowanie wiadomości ECIES")
    encrypted = ecies_encrypt(msg, bob_pub)

    print("Odszyfrowywanie ECIES")
    decrypted = ecies_decrypt(encrypted, bob_priv)

    print("Odszyfrowana wiadomość:", decrypted.decode())


if __name__ == "__main__":
    main()
