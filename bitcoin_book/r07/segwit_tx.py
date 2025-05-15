import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bitcoin_module.helper import *
import bitcoin_module.ecc_tests as ecc_tests
import bitcoin_module.misc_tests as misc_tests
from bitcoin_module.ecc import *
import hashlib

from io import BytesIO
from bitcoin_module.script import *

# from bitcoin_module.tx import *
from bitcoin_module.tx_segwit import *

import bitcoin_module.bech32_sipa as bech32_sipa
import logging

if __name__ == "__main__":
    
    logging.basicConfig(level=logging.INFO)

    logger_do_zmiany = logging.getLogger('bitcoin_module.script')
    logger_do_zmiany.setLevel(logging.WARNING)
    logger_do_zmiany = logging.getLogger('bitcoin_module.tx')
    logger_do_zmiany.setLevel(logging.WARNING)


    print('Tworzenie własnych transakcji w testnecie')
    print('Drugi adres')

    prev_tx_1 = bytes.fromhex('8cac2c4c30aca93ce157cb8428c0c398a7bbbf8ad7ddf9380dbc1f7626527e66')
    prev_index_1 = 1
    prev_tx_2 = bytes.fromhex('8e002ed019aa5931634d1cb3e4783089a279e163f4b17fa9a9cb2bdf47730d26')
    prev_index_2 = 2
    target_address = 'mnVxMqyVjWTxaUU1BJGUSQMTUWNk6LQqEA'
    target_amount = 0.000075
    
    passphrase = b'pbobinsk@gmail.com my another super secret pbobinski'
    secret = little_endian_to_int(hash256(passphrase))
    
    priv = PrivateKey(secret=secret)
    tx_ins = []
    tx_ins.append(TxIn(prev_tx_1, prev_index_1))
    tx_ins.append(TxIn(prev_tx_2, prev_index_2))
    tx_outs = []
    h160 = decode_base58(target_address)
    script_pubkey = p2pkh_script(h160)
    target_satoshis = int(target_amount*100000000)
    tx_outs.append(TxOut(target_satoshis, script_pubkey))
    tx_obj = Tx(1, tx_ins, tx_outs, 0, testnet=True)
    print(tx_obj.sign_input(0, priv))
    print(tx_obj.sign_input(1, priv))
    print('---')
    print(tx_obj.serialize().hex())
    print('---')
    print('tx fee')
    print(tx_obj.fee())
    print('tx fee end')
    print(target_satoshis)


    print('Tworzenie własnych transakcji w testnecie')
    print('To teraz na SegWit')
    prev_tx_1 = bytes.fromhex('1fabca255dd24e493fdbc37d6e1cb9302f92bd90157ad26973e7733c83c67a91')
    prev_index_1 = 0
    prev_tx_2 = bytes.fromhex('1700587abf5d6b721f0c67462cd35038b8e0817756b9d76e084651eae701c7c4')
    prev_index_2 = 0
    target_address = 'tb1qfjvgfchly0u77z9vh36jsttcvy2ehaxl2hnk86'
    target_amount = 0.00017
    passphrase = b'pbobinsk@gmail.com my super secret pbo'
    secret = little_endian_to_int(hash256(passphrase))
    
    priv = PrivateKey(secret=secret)
    tx_ins = []
    tx_ins.append(TxIn(prev_tx_1, prev_index_1))
    tx_ins.append(TxIn(prev_tx_2, prev_index_2))
    tx_outs = []

    # h160 = decode_base58(target_address)
    # 1. Zdekoduj adres Bech32 (P2WPKH) używając bech32_sipa.decode
    hrp_expected_testnet = "tb" # Human-readable part dla adresów SegWit na testnecie

    # Funkcja decode(hrp, addr) z bech32_sipa.py:
    # - hrp: oczekiwany human-readable part (np. "tb" dla testnet, "bc" dla mainnet)
    # - addr: adres Bech32 do zdekodowania
    # Zwraca: (witness_version, witness_program_bytes) lub (None, None) w przypadku błędu.
    decoded_address_data = bech32_sipa.decode(hrp_expected_testnet, target_address)

    if decoded_address_data == (None, None):
        raise ValueError(f"Niepoprawny adres SegWit ({target_address}) lub niezgodny HRP (oczekiwano '{hrp_expected_testnet}').")

    witness_version, program_witness_bytes_list = decoded_address_data

    # Sprawdź wersję witness i długość programu dla P2WPKH
    if witness_version != 0:
        # Ten kod obsługuje tylko P2WPKH (wersja 0).
        # Dla Taproot (P2TR) wersja witness byłaby 1, a typ kodowania Bech32m.
        raise ValueError(f"Nieobsługiwana wersja witness: {witness_version}. Oczekiwano 0 dla P2WPKH.")

    if len(program_witness_bytes_list) != 20:
        # Dla P2WPKH, program witness to 20-bajtowy HASH160(skompresowany_klucz_publiczny)
        raise ValueError(f"Niepoprawna długość programu witness dla P2WPKH: {len(program_witness_bytes_list)} bajtów. Oczekiwano 20.")

    program_witness_bytes = bytes(program_witness_bytes_list)

    # h160_from_segwit_address to nasz `program_witness_bytes`
    print(f"Zdekodowany program witness (h160) z adresu SegWit: {program_witness_bytes.hex()}")


    # script_pubkey = p2pkh_script(h160)
    # 2. Stwórz scriptPubKey dla P2WPKH
    #    scriptPubKey to: OP_0 <program_witness_bytes>
    script_pubkey_p2wpkh = p2wpkh_script(program_witness_bytes)

    target_satoshis = int(target_amount*100000000)
    # tx_outs.append(TxOut(target_satoshis, script_pubkey))
    
    # 3. Stwórz obiekt TxOut
    tx_outs.append(TxOut(target_satoshis, script_pubkey_p2wpkh))
    
    
    tx_obj = Tx(1, tx_ins, tx_outs, 0, testnet=True)

    print(f"\nUtworzony ScriptPubKey dla adresu SegWit ({target_address}):")
    print(f"  {script_pubkey_p2wpkh.serialize().hex()}")
    print(f"  Elementy skryptu: {script_pubkey_p2wpkh.cmds}") # Powinno być [0, <20_bajtów_hash>]

    print(tx_obj.sign_input(0, priv))
    print(tx_obj.sign_input(1, priv))
    print('--- skopiować')
    print(tx_obj.serialize().hex())
    print('---')
    print('tx fee')
    print(tx_obj.fee())
    print('tx fee end')
    print(target_satoshis)
    
    