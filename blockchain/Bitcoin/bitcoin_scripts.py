import os, sys
from io import BytesIO
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../bitcoin_book")))
from bitcoin_module.tx import TxFetcher
from bitcoin_module.script import Script 
from bitcoin_module.helper import encode_varint, hash160, int_to_little_endian, SIGHASH_ALL
from bitcoin_module.ecc import PrivateKey

import logging


logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout, # Upewnij się, że logi pojawią się w Twojej konsoli
)

if __name__ == "__main__":
    

    # scriptPubKey: OP_HASH160 <hash160> OP_EQUAL
    # surowe bajty: a9 14 <20-bajtowy_hash> 87

    print('=====================')
    print('Prosty skrypt: ', 'scriptPubKey: OP_HASH160 <hash160> OP_EQUAL')

    # Jakiś przykładowy hash160
    tr = b'Jakas transakcja'
    print(f'Treść: {tr}')
    print(f'Hex: {tr.hex()}')
    h160 = hash160(tr) # 20 bajtów
    print(f'Hash160: {h160.hex()}')
    raw_script_pubkey = bytes([0xa9, 0x14]) + h160 + bytes([0x87])
    # Musimy dodać na początku długość skryptu jako varint
    # Długość to 1 (OP_HASH160) + 1 (OP_PUSHBYTES_20) + 20 (hash) + 1 (OP_EQUAL) = 23 bajty
    script_with_len = encode_varint(len(raw_script_pubkey)) + raw_script_pubkey
    Script.print_all(script_with_len)

    s1 = Script([0xa9, h160, 0x87])
    s2 = Script([tr])
    print(f'Ewaluacja: {(s2+s1).evaluate(0)}')

    print('Test https://scrypt.studio/')
    print('Locking Script: reprezentacja')
    print('Unocking Script: Hex transakcji')


    print('=====================')
    print('Prosty skrypt: ', 'scriptPubKey: OP_DUP OP_DUP OP_MUL OP_ADD OP_6 OP_EQUAL')
    print('Unlock skrypt: ', 'scriptSig: OP_2')
    
    script_pubkey = Script([0x76, 0x76, 0x95, 0x93, 0x56, 0x87])
    script_sig = Script([0x52])
    combined_script = script_sig + script_pubkey
    print(f'Ewaluacja: {combined_script.evaluate(0)}')
    Script.print_all(script_pubkey.serialize())
    Script.print_all(script_sig.serialize())
    
    print('Test https://scrypt.studio/')
    print('Locking Script: pubkey')
    print('Unocking Script: sig')
    
    

    print('=====================')
    print('Skrypt testujący Hash160: ', 'script: OP_2DUP OP_EQUAL OP_NOT OP_VERIFY OP_SHA1 OP_SWAP OP_SHA1 OP_EQUAL')
    print('Unlock skrypt: ', 'scriptSig: dwie wartości')


    script_hex = '6e879169a77ca787'
    script_bytes = bytes.fromhex(script_hex)
    vi = encode_varint(len(script_bytes))

    script = Script.parse(BytesIO(vi+bytes.fromhex(script_hex)))
    Script.print_all(script.serialize())
    
    c1 = '255044462d312e330a25e2e3cfd30a0a0a312030206f626a0a3c3c2f57696474682032203020522f4865696768742033203020522f547970652034203020522f537562747970652035203020522f46696c7465722036203020522f436f6c6f7253706163652037203020522f4c656e6774682038203020522f42697473506572436f6d706f6e656e7420383e3e0a73747265616d0affd8fffe00245348412d3120697320646561642121212121852fec092339759c39b1a1c63c4c97e1fffe017f46dc93a6b67e013b029aaa1db2560b45ca67d688c7f84b8c4c791fe02b3df614f86db1690901c56b45c1530afedfb76038e972722fe7ad728f0e4904e046c230570fe9d41398abe12ef5bc942be33542a4802d98b5d70f2a332ec37fac3514e74ddc0f2cc1a874cd0c78305a21566461309789606bd0bf3f98cda8044629a1'
    c2 = '255044462d312e330a25e2e3cfd30a0a0a312030206f626a0a3c3c2f57696474682032203020522f4865696768742033203020522f547970652034203020522f537562747970652035203020522f46696c7465722036203020522f436f6c6f7253706163652037203020522f4c656e6774682038203020522f42697473506572436f6d706f6e656e7420383e3e0a73747265616d0affd8fffe00245348412d3120697320646561642121212121852fec092339759c39b1a1c63c4c97e1fffe017346dc9166b67e118f029ab621b2560ff9ca67cca8c7f85ba84c79030c2b3de218f86db3a90901d5df45c14f26fedfb3dc38e96ac22fe7bd728f0e45bce046d23c570feb141398bb552ef5a0a82be331fea48037b8b5d71f0e332edf93ac3500eb4ddc0decc1a864790c782c76215660dd309791d06bd0af3f98cda4bc4629b1'

    collision1 = bytes.fromhex(c1)  
    collision2 = bytes.fromhex(c2)
    script_sig = Script([collision1, collision2])
    combined_script = script_sig + script
    print(f'Ewaluacja: {combined_script.evaluate(0)}')
    Script.print_all(script_sig.serialize())
    print('Test https://scrypt.studio/')
    print('Locking Script: pubkey')
    print('Unocking Script: sig')
    
    print('=====================')
    print('Skrypt MultiSig: ')
    print('Unlock skrypt: podpisy')


    # Generujemy klucze dla dwóch uczestników: Alicji i Boba
    priv_key_alicja = PrivateKey(101)
    pub_key_alicja = priv_key_alicja.point.sec(compressed=True)

    priv_key_bob = PrivateKey(102)
    pub_key_bob = priv_key_bob.point.sec(compressed=True)

    print("--- Klucze Uczestników ---")
    print(f"Klucz publiczny Alicji (hex): {pub_key_alicja.hex()}")
    print(f"Klucz publiczny Boba (hex):   {pub_key_bob.hex()}")

# Skrypt multisig 2-z-2: OP_2 <pub_A> <pub_B> OP_2 OP_CHECKMULTISIG
    redeem_script_cmds = [
        0x52,            # OP_2 (2 wymagane podpisy)
        pub_key_alicja,
        pub_key_bob,
        0x52,            # OP_2 (2 dostępne klucze)
        0xae             # OP_CHECKMULTISIG
    ]
    redeem_script = Script(redeem_script_cmds)
    print(f"\nRedeemScript (logiczny): {redeem_script}")


    # Potrzebujemy jego serializowanej formy, aby obliczyć hash
    redeem_script_serialized = redeem_script.serialize()
    # Właściwy hash160 jest liczony na pełnej, serializowanej formie skryptu,
    # która w tym przypadku jest taka sama jak `raw_serialize`
    h160 = hash160(redeem_script.raw_serialize()) 

    # scriptPubKey P2SH: OP_HASH160 <hash160(RedeemScript)> OP_EQUAL
    locking_script_cmds = [0xa9, h160, 0x87]
    locking_script = Script(locking_script_cmds) # To jest nasz scriptPubKey
    print(f"Locking Script (P2SH, scriptPubKey): {locking_script}")

    # Musimy mieć hash transakcji (z), który zostanie podpisany.
    # Dla celów demonstracji, użyjemy dowolnej wartości.
    z = int.from_bytes(b'Symulowany hash transakcji', 'big')

    # Alicja i Bob podpisują ten sam hash
    podpis_alicja = priv_key_alicja.sign(z)
    podpis_bob = priv_key_bob.sign(z)

    # Konwertujemy podpisy do formatu DER (bez SIGHASH - to oczekiwane przez OP_CHECKMULTISIG)
    der_alicja = podpis_alicja.der()+ int_to_little_endian(SIGHASH_ALL, 1)
    der_bob = podpis_bob.der()+ int_to_little_endian(SIGHASH_ALL, 1)

    # scriptSig dla P2SH multisig: OP_0 <sig_A> <sig_B> <RedeemScript_serializowany>
    unlocking_script_cmds = [
        0x00, # OP_0 dla OP_CHECKMULTISIG
        der_alicja,
        der_bob,
        redeem_script.raw_serialize() # Ważne: dodajemy surowy, serializowany redeem_script
    ]
    unlocking_script = Script(unlocking_script_cmds) # To jest nasz scriptSig
    print(f"\nUnlocking Script (scriptSig): {unlocking_script}")

    print("\n--- Rozpoczynam Weryfikację P2SH ---")

    # ETAP 1: Weryfikacja standardowa (sprawdzenie hasha RedeemScript)
    print("\nETAP 1: Weryfikacja, czy hash(RedeemScript) pasuje do Locking Script...")
    combined_script_etap1 = unlocking_script + locking_script
    etap1_result = combined_script_etap1.evaluate(z)
    print(f"Wynik Etapu 1: {etap1_result}")

    if not etap1_result:
        print("BŁĄD: Weryfikacja P2SH nie powiodła się na pierwszym etapie.")
    else:
        print("Etap 1 zakończony sukcesem. Przechodzę do Etapu 2.")
        
        # ETAP 2: Wykonanie RedeemScript
        print("\nETAP 2: Wykonanie RedeemScript z dostarczonymi podpisami...")
        
        # Przygotowanie stosu dla drugiego etapu
        # Pobieramy elementy z Unlocking Script, które NIE SĄ RedeemScriptem
        elementy_dla_redeem_script = unlocking_script.cmds[:-1]
        
        # Tworzymy "wirtualny" unlocking script dla drugiego etapu
        unlocking_script_etap2 = Script(elementy_dla_redeem_script)
        
        # Łączymy go z RedeemScript (który teraz działa jak locking script)
        combined_script_etap2 = unlocking_script_etap2 + redeem_script
        
        # Ewaluacja
        etap2_result = combined_script_etap2.evaluate(z)
        
        print(f"Wynik Etapu 2: {etap2_result}")

        if etap2_result:
            print("\n\033[92mSUKCES! Pełna weryfikacja P2SH zakończona pomyślnie.\033[0m")
        else:
            print("\n\033[91mBŁĄD: Weryfikacja P2SH nie powiodła się na drugim etapie.\033[0m")

    print('Test RedeemScript https://scrypt.studio/')
    print('Locking Script')
    print('Unocking Script')


    print('Test https://scrypt.studio/')
    print('Locking Script - Redeem')
    print('Unocking Script bez RedeemScript')
# OP_2 02311091dd9860e8e20ee13473c1155f5f69635e394704eaa74009452246cfa9b3 023049f7ffc71d744bd9bed6f42dc6a28974e3a1b9d30671f800e5d46389103c7e OP_2 OP_CHECKMULTISIG 
# OP_0 304402205736c6b31132fa1b7c0d6fe2892735cb580d027a27093b1fc5f1a97366ea28210220183158420d890322424f6a00b71eff2ec3236d6bf23eb3d46ac26fd03005ac2801 3044022050936ddc71f7e3b818e1a3f8e6dd8b71db22d0a964c88ab58601e5640ba0cb7d022071a2e439d384afdddaa948a1269efd9bc940ceca57e5290ca8bd3075472691c601
    print('Test https://siminchen.github.io/bitcoinIDE/build/editor.html')
    print('Jeden Script: Unlock + Lock')
# OP_0 304402205736c6b31132fa1b7c0d6fe2892735cb580d027a27093b1fc5f1a97366ea28210220183158420d890322424f6a00b71eff2ec3236d6bf23eb3d46ac26fd03005ac2801 3044022050936ddc71f7e3b818e1a3f8e6dd8b71db22d0a964c88ab58601e5640ba0cb7d022071a2e439d384afdddaa948a1269efd9bc940ceca57e5290ca8bd3075472691c601 OP_2 02311091dd9860e8e20ee13473c1155f5f69635e394704eaa74009452246cfa9b3 023049f7ffc71d744bd9bed6f42dc6a28974e3a1b9d30671f800e5d46389103c7e OP_2 OP_CHECKMULTISIG