import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../bitcoin_book")))
from bitcoin_module.ecc import PrivateKey, PublicKey, generate_p2wpkh_address
from bitcoin_module.helper import hash256, little_endian_to_int
import hashlib

if __name__ == "__main__":
    
    # Przykładowa wiadomość
    message = "Hello, Bitcoin!"
    print(f"Wiadomość: ={message}")

    # Obliczamy hash SHA256 wiadomości
    z = int.from_bytes(hashlib.sha256(message.encode()).digest(), 'big')
    print(f"Hash wiadomości: ={z}")


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

    print("Generujemy adresy")


    passphrase = b'imie@email.com my super secret passphrase'
    secret = little_endian_to_int(hash256(passphrase))
    priv = PrivateKey(secret)
    print("Portfel 1")
    print("Address Testnet 1")
    print(priv.point.address(testnet=True))
    print(priv.point.address_segwit_p2wpkh(testnet=True))
    print(generate_p2wpkh_address(secret,testnet=True))
    wif_testnet = priv.wif(compressed=True, testnet=True)
    print(f"Private Key WIF 1 (Testnet, Compressed): {wif_testnet}")


    print('Portfel 2')
    passphrase = b'inne_imie@email.com my another super secret passphrase'
    secret = little_endian_to_int(hash256(passphrase))
    priv = PrivateKey(secret)
    print("Address Testnet 2")
    print(priv.point.address(testnet=True))
    print(priv.point.address_segwit_p2wpkh(testnet=True))
    print(generate_p2wpkh_address(secret,testnet=True))
    wif_testnet = priv.wif(compressed=True, testnet=True)
    print(f"Private Key WIF 2 (Testnet, Compressed): {wif_testnet}")