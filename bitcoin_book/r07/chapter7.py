import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bitcoin_module.helper import *
import bitcoin_module.ecc_tests as ecc_tests
import bitcoin_module.misc_tests as misc_tests
from bitcoin_module.ecc import *
import hashlib

from io import BytesIO
from bitcoin_module.script import *

from bitcoin_module.tx import *
# from bitcoin_module.tx_segwit import *

import bitcoin_module.bech32_sipa as bech32_sipa
import logging

if __name__ == "__main__":
    
    logging.basicConfig(level=logging.INFO)


    logger_do_zmiany = logging.getLogger('bitcoin_module.script')
    logger_do_zmiany.setLevel(logging.WARNING)
    logger_do_zmiany = logging.getLogger('bitcoin_module.tx')
    logger_do_zmiany.setLevel(logging.WARNING)

    print('Testy z poprzednich rozdziałów')
    # run_all(ecc_tests.ECCTest)
    # run_all(ecc_tests.S256Test)
    # run_all(ecc_tests.PrivateKeyTest)
    # run_all(ecc_tests.SignatureTest)
    # run_all(misc_tests.HelperTest)
    # run_all(misc_tests.TxTest)
    # run_all(misc_tests.OpTest)
    # run_all(misc_tests.ScriptTest)

    print('Rozdział 7')

    print('Sprawdzanie sumy wejść i sumy wyjść')

    raw_tx = ('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
    stream = BytesIO(bytes.fromhex(raw_tx))
    transaction = Tx.parse(stream)
    print(transaction.fee() >= 0)

    print('Sprawdzanie podpisu')

    sec = bytes.fromhex('0349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278a')
    der = bytes.fromhex('3045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed')
    z = 0x27e0c5994dec7824e56dec6b2fcb342eb7cdb0d0957c2fce9882f715e85d81a6
    point = S256Point.parse(sec)
    signature = Signature.parse(der)
    print(point.verify(z, signature))

    modified_tx = bytes.fromhex('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000001976a914a802fc56c704ce87c42d7c92eb75e7896bdc41ae88acfeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac1943060001000000')
    h256 = hash256(modified_tx)
    z = int.from_bytes(h256, 'big')
    print(hex(z))

    sec = bytes.fromhex('0349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278a')
    der = bytes.fromhex('3045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed')
    # z = 0x27e0c5994dec7824e56dec6b2fcb342eb7cdb0d0957c2fce9882f715e85d81a6
    point = S256Point.parse(sec)
    signature = Signature.parse(der)
    print(point.verify(z, signature))

    run(misc_tests.TxTest("test_sig_hash"))

    tx = TxFetcher.fetch('452c629d67e41baec3ac6f04fe744b4b9617f8f859c63b3002f8684e7a4fee03')
    print(len(tx.tx_ins))
    print(len(tx.tx_outs))
    print(tx.sig_hash(0))
    # tx = TxFetcher.fetch('bb41a757f405890fb0f5856228e23b715702d714d59bf2b1feb70d8b2b4e3e08')
    print(len(tx.tx_ins))
    print(len(tx.tx_outs))
    print(tx.sig_hash(0))


    run(misc_tests.TxTest("test_verify_p2pkh"))

    

    tx = TxFetcher.fetch('452c629d67e41baec3ac6f04fe744b4b9617f8f859c63b3002f8684e7a4fee03')
    print(tx.verify())
    # tx = TxFetcher.fetch('5e253ce1bb82c0bd1133bb7ec8dee09cbe50df12de3a5f393e2a03a1242f88dd')
    print(len(tx.tx_ins))
    v = tx.verify()
    print(v)

    print('Tworzenie transakcji')

    prev_tx = bytes.fromhex('0d6fe5213c0b3291f208cba8bfb59b7476dffacc4e5cb66f6eb20a080843a299')
    prev_index = 13
    tx_in = TxIn(prev_tx, prev_index)
    tx_outs = []
    change_amount = int(0.33*100000000)
    change_h160 = decode_base58('mzx5YhAH9kNHtcN481u6WkjeHjYtVeKVh2')
    change_script = p2pkh_script(change_h160)
    change_output = TxOut(amount=change_amount, script_pubkey=change_script)
    target_amount = int(0.1*100000000)
    target_h160 = decode_base58('mnrVtF8DWjMu839VW3rBfgYaAfKk8983Xf')
    target_script = p2pkh_script(target_h160)
    target_output = TxOut(amount=target_amount, script_pubkey=target_script)
    tx_obj = Tx(1, [tx_in], [change_output, target_output], 0, True)
    print(tx_obj)
    print(tx_obj.serialize().hex())
    # print(tx_obj.fee())
    

    print('Podpisanie transakcji')

    # transaction = tx_obj

    z = transaction.sig_hash(0)
    private_key = PrivateKey(secret=8675309)
    der = private_key.sign(z).der()
    sig = der + SIGHASH_ALL.to_bytes(1, 'big')
    sec = private_key.point.sec()
    script_sig = Script([sig, sec])
    transaction.tx_ins[0].script_sig = script_sig 
    print('hex')
    print(transaction.serialize().hex())
    print('tx fee')
    print(transaction.fee())
    print('tx fee end')
    print(target_amount + change_amount)
    

    run_all(misc_tests.TxTest)

    print('Tworzenie własnych transakcji w testnecie')
    print('Z książki')

    prev_tx = bytes.fromhex('75a1c4bc671f55f626dda1074c7725991e6f68b8fcefcfca7b64405ca3b45f1c')
    prev_index = 1
    target_address = 'miKegze5FQNCnGw6PKyqUbYUeBa4x2hFeM'
    target_amount = 0.01
    change_address = 'mzx5YhAH9kNHtcN481u6WkjeHjYtVeKVh2'
    change_amount = 0.009
    secret = 8675309
    priv = PrivateKey(secret=secret)
    tx_ins = []
    tx_ins.append(TxIn(prev_tx, prev_index))
    tx_outs = []
    h160 = decode_base58(target_address)
    script_pubkey = p2pkh_script(h160)
    target_satoshis = int(target_amount*100000000)
    tx_outs.append(TxOut(target_satoshis, script_pubkey))
    h160 = decode_base58(change_address)
    script_pubkey = p2pkh_script(h160)
    change_satoshis = int(change_amount*100000000)
    tx_outs.append(TxOut(change_satoshis, script_pubkey))
    tx_obj = Tx(1, tx_ins, tx_outs, 0, testnet=True)
    print(tx_obj.sign_input(0, priv))
 
    print(tx_obj.serialize().hex())

    print('tx fee')
    print(tx_obj.fee())
    print('tx fee end')
    print(target_satoshis + change_satoshis)


    print('Tworzenie własnych transakcji w testnecie')
    print('Moje')

    prev_tx = bytes.fromhex('e0c735327a36c876110b9ca2912a09d64ffa25c3659c632c6eb6f84535abbf7a')
    prev_index = 1
    target_address = 'miKegze5FQNCnGw6PKyqUbYUeBa4x2hFeM'
    target_amount = 0.0006
    change_address = 'mgU39Z5p3fpbDUrZ7uqg3mJj9E29fHG4aw'
    change_amount = 0.0003
    
    passphrase = b'pbobinsk@gmail.com my super secret pbo'
    secret = little_endian_to_int(hash256(passphrase))
    
    priv = PrivateKey(secret=secret)
    tx_ins = []
    tx_ins.append(TxIn(prev_tx, prev_index))
    tx_outs = []
    h160 = decode_base58(target_address)
    script_pubkey = p2pkh_script(h160)
    target_satoshis = int(target_amount*100000000)
    tx_outs.append(TxOut(target_satoshis, script_pubkey))
    h160 = decode_base58(change_address)
    script_pubkey = p2pkh_script(h160)
    change_satoshis = int(change_amount*100000000)
    tx_outs.append(TxOut(change_satoshis, script_pubkey))
    tx_obj = Tx(1, tx_ins, tx_outs, 0, testnet=True)
    print(tx_obj.sign_input(0, priv))
    print('---')
    print(tx_obj.serialize().hex())
    print('---')
    print('tx fee')
    print(tx_obj.fee())
    print('tx fee end')
    print(target_satoshis + change_satoshis)


    print('Tworzenie własnych transakcji w testnecie')
    print('Moje ambitne')

    prev_tx_1 = bytes.fromhex('0b30e0b7eaa2ca7d2cb09587938ad663e3cb71e1724bb0a2728f4e7808ab73c2')
    prev_index_1 = 1
    prev_tx_2 = bytes.fromhex('5ddfa866650dcc613f1ea9b72305feeeba5b1629d44d597365c97ebdfe6f66ca')
    prev_index_2 = 0
    target_address = 'mgU39Z5p3fpbDUrZ7uqg3mJj9E29fHG4aw'
    target_amount = 0.00035
    
    passphrase = b'pbobinsk@gmail.com my super secret pbo'
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
    print(target_satoshis + change_satoshis)


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
    print(target_satoshis + change_satoshis)


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
    
    