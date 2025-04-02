import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bitcoin_module.helper import run, run_all, hash256, little_endian_to_int
import bitcoin_module.ecc_tests as ecc_tests
from bitcoin_module.ecc import PrivateKey, PublicKey
import hashlib

if __name__ == "__main__":
    

    run_all(ecc_tests.ECCTest)

    run_all(ecc_tests.S256Test)

    run_all(ecc_tests.PrivateKeyTest)

    run_all(ecc_tests.SignatureTest)

    run_all(ecc_tests.HelperTest)


# Przykładowa wiadomość
message = "Hello, Bitcoin!"

# Obliczamy hash SHA256 wiadomości
z = int.from_bytes(hashlib.sha256(message.encode()).digest(), 'big')

# Tworzymy klucz prywatny (sekretna liczba)
secret = 0x1A2B3C4D5E6F7890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890  # przykładowy klucz prywatny
priv = PrivateKey(secret)

# Tworzymy podpis i klucz publiczny
signature = priv.sign(z)
pub = PublicKey(priv.point)

# Wyświetlamy podpis i kluczpubliczny
print(f"Podpis: (r={hex(signature.r)}, s={hex(signature.s)})")
print(f"Klucz publiczny: ={pub}")

# Sprawdzamy podpis
is_valid = pub.verify(z, signature)
print("Czy podpis jest poprawny?", is_valid)


print("PrivateKey")
print(priv)
print(priv.hex())
print(priv.wif())
print(priv.wif(testnet=True))
print(priv.wif(compressed=False))
print(priv.wif(compressed=False,testnet=True))


print("PublicKey")
print(pub)
print(pub.point.sec())
print(pub.point.sec(compressed=False))
print(pub.point.address())
print(pub.point.address(compressed=False))
print(pub.point.address(testnet=True))
print(pub.point.address(compressed=False,testnet=True))

print("Signature")
print(signature.der())

passphrase = b'pbobinsk@gmail.com my super secret pbo'
secret = little_endian_to_int(hash256(passphrase))
priv = PrivateKey(secret)
print("Address Testnet")
print(priv.point.address(testnet=True))