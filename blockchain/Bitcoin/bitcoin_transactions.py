import os, sys
from io import BytesIO
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../bitcoin_book")))
from bitcoin_module.tx import TxFetcher
from bitcoin_module.script import Script 
from bitcoin_module.helper import encode_varint, hash160, int_to_little_endian, SIGHASH_ALL
from bitcoin_module.ecc import PrivateKey


if __name__ == "__main__":
    
    cache_file = './tx.cache'
    fetched_tx_1 = TxFetcher.fetch('4254b23e407dcdbebb50f0f1282fd5efe509e9cf0392a3882fe046822b08be90')
    fetched_tx_2 = TxFetcher.fetch('55264f4d072df872a3d48038cd5dd4885565c0cc3d25577c4492785899a901d2')
    fetched_tx_3 = TxFetcher.fetch('df84650a6301418de871052350513695f881c9713f75ae516c6881fb2ad9dd4d')
    fetched_tx_4 = TxFetcher.fetch('f4566ae9e668de340aab0f69d3c41c11ae85d3f45ced46a410917aec3ec44fc1')
    TxFetcher.dump_cache(cache_file)


    print('Transakcja 1')
    print(fetched_tx_1)
    print('Transakcja 2')
    print(fetched_tx_2)


    print('Test wypisywanie skryptu - przenieść do innego pliku')

    # Przygotujmy nasz skrypt P2SH
    # scriptPubKey: OP_HASH160 <hash160> OP_EQUAL
    # surowe bajty: a9 14 <20-bajtowy_hash> 87

    print('Prosty skrypt: ', 'scriptPubKey: OP_HASH160 <hash160> OP_EQUAL')

    # Jakiś przykładowy hash160
    rs = b'935a87'
    print(rs)
    print(rs.hex())
    h160 = hash160(rs) # 20 bajtów
    print(h160.hex())
    # Tworzymy surowy skrypt binarny
    raw_script_pubkey = bytes([0xa9, 0x14]) + h160 + bytes([0x87])
    # Musimy dodać na początku długość skryptu jako varint
    # Długość to 1 (OP_HASH160) + 1 (OP_PUSHBYTES_20) + 20 (hash) + 1 (OP_EQUAL) = 23 bajty
    script_with_len = encode_varint(len(raw_script_pubkey)) + raw_script_pubkey
    Script.print_all(script_with_len)

    print('Bardziej złożony')
# 52: OP_2
# 21: OP_PUSHBYTES_33 (dla klucza Alicji)
# 0253...c09: 33-bajtowy klucz publiczny Alicji
# 21: OP_PUSHBYTES_33 (dla klucza Boba)
# 02e3...c73: 33-bajtowy klucz publiczny Boba
# 21: OP_PUSHBYTES_33 (dla klucza Karoliny)
# 03a3...637: 33-bajtowy klucz publiczny Karoliny
# 53: OP_3
# ae: OP_CHECKMULTISIG

    print('Generuję klucze')
    priv_key_alicja = PrivateKey(101)
    pub_key_alicja = priv_key_alicja.point
    priv_key_bob = PrivateKey(102)
    pub_key_bob = priv_key_bob.point
    priv_key_karolina = PrivateKey(103)
    pub_key_karolina = priv_key_karolina.point

    sec_alicja = pub_key_alicja.sec(compressed=True)
    sec_bob = pub_key_bob.sec(compressed=True)
    sec_karolina = pub_key_karolina.sec(compressed=True)

    print("--- Dane dla Multisig 2-z-3 ---")
    print(f"Klucz pub. Alicji (SEC): {sec_alicja.hex()}")
    print(f"Klucz pub. Boba (SEC):   {sec_bob.hex()}")
    print(f"Klucz pub. Karoliny (SEC): {sec_karolina.hex()}")

# 2. Stwórz RedeemScript
# Składnia: OP_2 <pub_A> <pub_B> <pub_K> OP_3 OP_CHECKMULTISIG
# OP_2 to 0x52, OP_3 to 0x53, OP_CHECKMULTISIG to 0xae
# Każdy klucz pub. (33 bajty) jest poprzedzony opcodem OP_PUSHBYTES_33 (0x21)
    redeem_script_cmds = [
    0x52,            # OP_2 (m - liczba wymaganych podpisów)
    sec_alicja,
    sec_bob,
    sec_karolina,
    0x53,            # OP_3 (n - liczba dostępnych kluczy publicznych)
    0xae             # OP_CHECKMULTISIG
    ]

# Tworzymy obiekt Script z tej listy komend
    redeem_script_obj = Script(redeem_script_cmds)

# Serializujemy go do formatu binarnego, aby móc go sparsować
    raw_redeem_script = redeem_script_obj.serialize()
    print(f"\nSurowy RedeemScript (hex): {raw_redeem_script.hex()}")
    print(f"\nSurowy RedeemScript hash160: {hash160(raw_redeem_script).hex()}")
    

# Dodajemy długość skryptu na początku (varint)
    script_with_len = encode_varint(len(raw_redeem_script)) + raw_redeem_script
    print(f"\nPełny z długością RedeemScript (hex): {script_with_len.hex()}")

    script_hex = raw_redeem_script  
    Script.print_all(script_hex)


    print('Dalej skrypty')

    
# 56 = OP_6
# 76 = OP_DUP
# 87 = OP_EQUAL
# 93 = OP_ADD
# 95 = OP_MUL
    script_pubkey = Script([0x76, 0x76, 0x95, 0x93, 0x56, 0x87])
    script_sig = Script([82])
    combined_script = script_sig + script_pubkey
    print(combined_script.evaluate(0))

    script_hex = '6e879169a77ca787'
    script_bytes = bytes.fromhex(script_hex)
    length = len(script_bytes)  
    print(length)
    vi = encode_varint(length)
    print(vi)

    s = Script.parse(BytesIO(vi+bytes.fromhex('6e879169a77ca787')))

    Script.print_all(vi+bytes.fromhex('6e879169a77ca787'))

    c1 = '255044462d312e330a25e2e3cfd30a0a0a312030206f626a0a3c3c2f57696474682032203020522f4865696768742033203020522f547970652034203020522f537562747970652035203020522f46696c7465722036203020522f436f6c6f7253706163652037203020522f4c656e6774682038203020522f42697473506572436f6d706f6e656e7420383e3e0a73747265616d0affd8fffe00245348412d3120697320646561642121212121852fec092339759c39b1a1c63c4c97e1fffe017f46dc93a6b67e013b029aaa1db2560b45ca67d688c7f84b8c4c791fe02b3df614f86db1690901c56b45c1530afedfb76038e972722fe7ad728f0e4904e046c230570fe9d41398abe12ef5bc942be33542a4802d98b5d70f2a332ec37fac3514e74ddc0f2cc1a874cd0c78305a21566461309789606bd0bf3f98cda8044629a1'
    c2 = '255044462d312e330a25e2e3cfd30a0a0a312030206f626a0a3c3c2f57696474682032203020522f4865696768742033203020522f547970652034203020522f537562747970652035203020522f46696c7465722036203020522f436f6c6f7253706163652037203020522f4c656e6774682038203020522f42697473506572436f6d706f6e656e7420383e3e0a73747265616d0affd8fffe00245348412d3120697320646561642121212121852fec092339759c39b1a1c63c4c97e1fffe017346dc9166b67e118f029ab621b2560ff9ca67cca8c7f85ba84c79030c2b3de218f86db3a90901d5df45c14f26fedfb3dc38e96ac22fe7bd728f0e45bce046d23c570feb141398bb552ef5a0a82be331fea48037b8b5d71f0e332edf93ac3500eb4ddc0decc1a864790c782c76215660dd309791d06bd0af3f98cda4bc4629b1'

    collision1 = bytes.fromhex(c1)  # <1>
    collision2 = bytes.fromhex(c2)
    script_sig = Script([collision1, collision2])
    combined_script = script_sig + s
    print(combined_script.evaluate(0))

    full_script_bytes = script_sig.serialize()
    hex_stream_to_parse = full_script_bytes.hex()
    Script.print_all(full_script_bytes)

# https://scrypt.studio/