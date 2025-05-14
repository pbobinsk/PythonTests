import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Zaimportuj funkcje z lokalnego pliku (np. nazwanego bech32_sipa.py)
# Ten plik zawiera zarówno logikę Bech32, jak i funkcje SegWit encode/decode
try:
    # Załóżmy, że plik, który wkleiłeś, zapisałeś jako 'bech32_sipa.py'
    # Funkcje encode i decode na końcu tego pliku są tymi, których chcemy użyć
    from bitcoin_module.bech32_sipa import encode as sipa_full_encode, decode as sipa_full_decode 
    print("--- Zaimportowano funkcje z lokalnego pliku bech32_sipa.py ---")
except ImportError as e:
    print(f"BŁĄD: Nie można zaimportować funkcji z pliku bech32_sipa.py: {e}")
    print("Upewnij się, że plik zawierający implementację Sipy (ten, który wkleiłeś) ")
    print("nazywa się 'bech32_sipa.py' i znajduje się w tym samym katalogu co ten skrypt.")
    exit()
except Exception as e_other: # Na wszelki wypadek
    print(f"Nieoczekiwany błąd podczas importu: {e_other}")
    exit()


print(f"\n--- Test modułu bech32_sipa.py (kompletna implementacja Sipy) ---")

# --- Dane testowe dla P2WPKH Testnet (zgodne z BIP173) ---
hrp_expected = "tb"
witness_version_expected = 0
# Program świadka (HASH160 skompresowanego klucza publicznego) w bajtach (8-bit)
# To jest HASH160, który odpowiada adresowi tb1qw508d6qejxtdg4y5r3zarvary0c5xw7kxpjzsx
witness_program_bytes_expected = bytes.fromhex("751e76e8199196d454941c45d1b3a323f1433bd6")
# Oczekiwany adres Bech32
address_expected = "tb1qw508d6qejxtdg4y5r3zarvary0c5xw7kxpjzsx"

print(f"\n--- Testowanie KODOWANIA (sipa_full_encode) ---")
print(f"Dane wejściowe do kodowania:")
print(f"  HRP: '{hrp_expected}'")
print(f"  Wersja świadka: {witness_version_expected}")
print(f"  Program świadka (hex, 8-bit): {witness_program_bytes_expected.hex()}")

try:
    # Funkcja encode z końca pliku Sipy oczekuje:
    # encode(hrp, witver, witprog_jako_sekwencja_int_reprezentujących_bajty)
    encoded_address = sipa_full_encode(hrp_expected, witness_version_expected, witness_program_bytes_expected)
    print(f"  Wygenerowany adres Bech32: '{encoded_address}'")

    if encoded_address == address_expected:
        print("  KODOWANIE SUKCES: Wygenerowany adres jest zgodny z oczekiwanym!")
    else:
        print(f"  KODOWANIE BŁĄD: Wygenerowany adres ('{encoded_address}') różni się od oczekiwanego ('{address_expected}')!")
except Exception as e:
    print(f"  BŁĄD podczas sipa_full_encode: {e}")


print(f"\n--- Testowanie DEKODOWANIA (sipa_full_decode) ---")
address_to_decode = address_expected
print(f"Adres wejściowy do dekodowania: '{address_to_decode}'")
print(f"Oczekiwany HRP przy dekodowaniu: '{hrp_expected}'")

try:
    # Funkcja decode z końca pliku Sipy oczekuje:
    # decode(hrp_oczekiwane, adres_string)
    # Zwraca: (witver, witprog_jako_lista_int_reprezentujących_bajty)
    decoded_witver, decoded_witprog_list_of_ints = sipa_full_decode(hrp_expected, address_to_decode)
    
    if decoded_witver is not None and decoded_witprog_list_of_ints is not None:
        # Konwertuj listę integerów z powrotem na obiekt bytes do łatwego porównania
        decoded_witprog_bytes = bytes(decoded_witprog_list_of_ints)

        print(f"  Zdekodowana Wersja Świadka: {decoded_witver}")
        print(f"  Zdekodowany Program Świadka (hex, 8-bit): {decoded_witprog_bytes.hex()}")

        if decoded_witver == witness_version_expected and decoded_witprog_bytes == witness_program_bytes_expected:
            print("  DEKODOWANIE SUKCES: Zdekodowane dane są zgodne z oczekiwanymi!")
        else:
            print(f"  DEKODOWANIE BŁĄD: Zdekodowane dane różnią się od oczekiwanych.")
            if decoded_witver != witness_version_expected:
                print(f"      Wersja: Oczekiwano {witness_version_expected}, otrzymano {decoded_witver}")
            if decoded_witprog_bytes != witness_program_bytes_expected:
                print(f"      Program: Oczekiwano {witness_program_bytes_expected.hex()}, otrzymano {decoded_witprog_bytes.hex()}")
    else:
         print(f"  DEKODOWANIE BŁĄD: sipa_full_decode zwróciło None lub niekompletne dane.")
except Exception as e:
    print(f"  BŁĄD podczas sipa_full_decode: {e}")