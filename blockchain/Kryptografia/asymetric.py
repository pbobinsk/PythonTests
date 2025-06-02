# --- Przykład dla 3.1: Szyfrowanie Asymetryczne (RSA) ---
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

def run_asymmetric_encryption_example():
    print("--- Szyfrowanie Asymetryczne (RSA) ---")

    # 1. Generowanie pary kluczy (Prywatny i Publiczny)
    # W praktyce klucz prywatny byłby bezpiecznie przechowywany
    private_key = rsa.generate_private_key(
        public_exponent=65537,  # Standardowy publiczny wykładnik
        key_size=2048            # Rozmiar klucza w bitach (bezpieczny)
    )
    public_key = private_key.public_key()

    # (Opcjonalnie) Serializacja kluczy do formatu PEM (do przechowywania/przesyłania)
    # private_pem = private_key.private_bytes(
    #     encoding=serialization.Encoding.PEM,
    #     format=serialization.PrivateFormat.PKCS8,
    #     encryption_algorithm=serialization.NoEncryption() # Dla przykładu bez hasła
    # )
    # print("\nKlucz Prywatny (fragment PEM):\n", private_pem.decode().splitlines()[0:3])

    # public_pem = public_key.public_bytes(
    #     encoding=serialization.Encoding.PEM,
    #     format=serialization.PublicFormat.SubjectPublicKeyInfo
    # )
    # print("\nKlucz Publiczny (fragment PEM):\n", public_pem.decode().splitlines()[0:3])

    # 2. Wiadomość do zaszyfrowania
    message_to_encrypt = b"To jest tajna wiadomosc dla blockchain!" # b"" oznacza bajty
    print(f"\nOryginalna wiadomość: {message_to_encrypt.decode()}")

    # 3. Szyfrowanie wiadomości kluczem publicznym odbiorcy (tutaj naszym własnym public_key)
    #    Używamy paddingu OAEP, który jest zalecany dla RSA.
    ciphertext = public_key.encrypt(
        message_to_encrypt,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    print(f"Zaszyfrowana wiadomość (szyfrogram): {ciphertext.hex()} (hex)")

    # 4. Deszyfrowanie wiadomości kluczem prywatnym odbiorcy
    #    Tylko posiadacz klucza prywatnego może to zrobić!
    decrypted_message = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    print(f"Odszyfrowana wiadomość: {decrypted_message.decode()}")

    assert message_to_encrypt == decrypted_message, "Coś poszło nie tak z szyfrowaniem/deszyfrowaniem!"
    print("Szyfrowanie i deszyfrowanie zakończone sukcesem!")
    print("--------------------------------------------------\n")

if __name__ == '__main__':
    run_asymmetric_encryption_example()