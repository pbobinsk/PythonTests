# --- Przykład dla 3.0: Szyfrowanie Symetryczne (AES-GCM) ---
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os # Dla generowania losowego klucza i nonce

def run_symmetric_encryption_example():
    print("--- Szyfrowanie Symetryczne (AES-GCM) ---")

    # 1. Wygenerowanie/Uzgodnienie wspólnego tajnego klucza
    #    W tym przykładzie po prostu generujemy losowy klucz.
    #    W PRAKTYCE, BEZPIECZNE UZGODNIENIE TEGO KLUCZA JEST GŁÓWNYM WYZWANIEM!
    shared_key = AESGCM.generate_key(bit_length=256) # 256-bitowy klucz AES
    aesgcm = AESGCM(shared_key)
    print(f"Wspólny tajny klucz (fragment): {shared_key[:8].hex()}...") # Tylko dla demonstracji, nie rób tego w produkcji!

    # 2. Wiadomość do zaszyfrowania (tekst jawny)
    plaintext = b"To jest wiadomosc symetrycznie szyfrowana."
    print(f"Tekst jawny: {plaintext.decode()}")

    # 3. (Opcjonalnie) Dodatkowe dane uwierzytelniające (Associated Data - AD)
    #    Te dane nie są szyfrowane, ale są uwierzytelniane (ich integralność jest chroniona).
    #    Mogą to być np. nagłówki pakietu.
    associated_data = b"naglowek_informacyjny_123"

    # 4. Generowanie Nonce (Number used once) - wartość jednorazowa
    #    Nonce musi być unikalne dla każdej operacji szyfrowania tym samym kluczem.
    #    Nie musi być tajne, może być przesłane razem z szyfrogramem.
    nonce = os.urandom(12) # Zalecana długość dla AES-GCM to 12 bajtów (96 bitów)
    print(f"Nonce (jawne): {nonce.hex()}")

    # 5. Szyfrowanie
    #    aesgcm.encrypt(nonce, plaintext, associated_data)
    #    Zwraca szyfrogram, który zawiera zaszyfrowane dane oraz tag uwierzytelniający.
    ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext, associated_data)
    print(f"Szyfrogram (z tagiem): {ciphertext_with_tag.hex()}")

    # Alicja wysyła Bobowi: ciphertext_with_tag, nonce (i associated_data, jeśli użyte)
    # Bob musi znać ten sam shared_key!

    # --- Po stronie Boba (odbiorcy) ---
    print("\n--- Po stronie Boba (odbiorcy) ---")
    # Bob używa tego samego shared_key, nonce i (jeśli dotyczy) associated_data

    # 6. Deszyfrowanie
    #    aesgcm.decrypt(nonce, ciphertext_with_tag, associated_data)
    #    Jeśli tag uwierzytelniający jest niepoprawny (np. dane zostały zmienione),
    #    funkcja rzuci wyjątek InvalidTag.
    try:
        decrypted_plaintext = aesgcm.decrypt(nonce, ciphertext_with_tag, associated_data)
        print(f"Odszyfrowany tekst jawny: {decrypted_plaintext.decode()}")
        assert plaintext == decrypted_plaintext, "Odszyfrowana wiadomość nie zgadza się!"
        print("Szyfrowanie i deszyfrowanie symetryczne (AES-GCM) zakończone sukcesem!")
    except Exception as e: # W cryptography.exceptions można złapać konkretnie InvalidTag
        print(f"BŁĄD DESZYFROWANIA: {e}")
        print("Możliwe przyczyny: zły klucz, zły nonce, lub dane/tag zostały zmodyfikowane.")

    # Przykład nieudanej weryfikacji (zmiana szyfrogramu)
    print("\nPróba deszyfrowania ze zmodyfikowanym szyfrogramem:")
    tampered_ciphertext = ciphertext_with_tag[:-1] + b'X' # Zmień ostatni bajt
    try:
        aesgcm.decrypt(nonce, tampered_ciphertext, associated_data)
    except Exception as e: # cryptography.exceptions.InvalidTag
        print(f"Spodziewany błąd deszyfrowania: {e} - integralność naruszona!")
        
    print("--------------------------------------------------\n")

if __name__ == '__main__':
    run_symmetric_encryption_example()