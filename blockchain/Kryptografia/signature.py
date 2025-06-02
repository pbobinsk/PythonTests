# --- Przykład dla 3.2: Podpisy Cyfrowe (RSA) ---
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature # Do obsługi błędnej weryfikacji

def run_digital_signature_example():
    print("--- Podpisy Cyfrowe (RSA) ---")

    # 1. Generowanie pary kluczy (lub użycie tej samej co w poprzednim przykładzie)
    #    Nadawca (Alicja) ma klucz prywatny, odbiorca (Bob) zna klucz publiczny Alicji.
    alice_private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    alice_public_key = alice_private_key.public_key()

    # 2. Wiadomość do podpisania przez Alicję
    message_to_sign = b"Alicja potwierdza te warunki umowy."
    print(f"Oryginalna wiadomość od Alicji: {message_to_sign.decode()}")

    # 3. Tworzenie podpisu cyfrowego przez Alicję (używając jej klucza PRYWATNEGO)
    #    Podpisujemy HASH wiadomości, a nie samą wiadomość.
    #    Używamy paddingu PSS, który jest zalecany dla podpisów RSA.
    signature = alice_private_key.sign(
        message_to_sign,  # Biblioteka 'cryptography' sama hashuje dane przed podpisaniem dla niektórych paddingów
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH # Maksymalna długość soli dla PSS
        ),
        hashes.SHA256() # Algorytm haszujący, który ma być użyty
    )
    print(f"Podpis cyfrowy Alicji: {signature.hex()} (hex)")

    # Alicja wysyła Bobowi: wiadomość ORAZ podpis.

    # 4. Weryfikacja podpisu przez Boba (używając klucza PUBLICZNEGO Alicji)
    print("\nBob weryfikuje podpis Alicji...")
    try:
        alice_public_key.verify(
            signature,
            message_to_sign, # Bob używa tej samej wiadomości, którą otrzymał
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("Weryfikacja podpisu ZAKOŃCZONA SUKCESEM! Wiadomość jest autentyczna i integralna.")
    except InvalidSignature:
        print("BŁĄD WERYFIKACJI! Podpis jest nieprawidłowy lub wiadomość została zmieniona.")

    # 5. Próba weryfikacji z zmienioną wiadomością (demonstracja integralności)
    print("\nBob próbuje zweryfikować podpis z ZMIENIONĄ wiadomością...")
    tampered_message = b"Alicja potwierdza te ZMIENIONE warunki umowy."
    print(f"Zmieniona wiadomość: {tampered_message.decode()}")
    try:
        alice_public_key.verify(
            signature, # Ten sam oryginalny podpis
            tampered_message, # Ale inna wiadomość
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("Weryfikacja ze zmienioną wiadomością ZAKOŃCZONA SUKCESEM! (TO NIE POWINNO SIĘ ZDARZYĆ)")
    except InvalidSignature:
        print("BŁĄD WERYFIKACJI! Podpis nie pasuje do zmienionej wiadomości. Integralność naruszona.")

    # 6. Próba weryfikacji z kluczem publicznym innej osoby (demonstracja autentyczności)
    print("\nBob próbuje zweryfikować podpis Alicji kluczem publicznym Ewy...")
    eve_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    eve_public_key = eve_private_key.public_key()
    try:
        eve_public_key.verify( # Klucz publiczny Ewy
            signature, # Oryginalny podpis Alicji
            message_to_sign, # Oryginalna wiadomość Alicji
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("Weryfikacja kluczem Ewy ZAKOŃCZONA SUKCESEM! (TO NIE POWINNO SIĘ ZDARZYĆ)")
    except InvalidSignature:
        print("BŁĄD WERYFIKACJI! Podpis Alicji nie pasuje do klucza publicznego Ewy. Autentyczność potwierdzona (negatywnie).")

    print("--------------------------------------------------\n")


if __name__ == '__main__':
    run_digital_signature_example()