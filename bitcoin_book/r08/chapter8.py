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

    print('Rozdział 8')


    modified_tx = bytes.fromhex('0100000001868278ed6ddfb6c1ed3ad5f8181eb0c7a385aa0836f01d5e4789e6bd304d87221a000000475221022626e955ea6ea6d98850c994f9107b036b1334f18ca8830bfff1295d21cfdb702103b287eaf122eea69030a0e9feed096bed8045c8b98bec453e1ffac7fbdbd4bb7152aeffffffff04d3b11400000000001976a914904a49878c0adfc3aa05de7afad2cc15f483a56a88ac7f400900000000001976a914418327e3f3dda4cf5b9089325a4b95abdfa0334088ac722c0c00000000001976a914ba35042cfe9fc66fd35ac2224eebdafd1028ad2788acdc4ace020000000017a91474d691da1574e6b3c192ecfb52cc8984ee7b6c56870000000001000000')
    h256 = hash256(modified_tx)
    z = int.from_bytes(h256, 'big')
    sec = bytes.fromhex('022626e955ea6ea6d98850c994f9107b036b1334f18ca8830bfff1295d21cfdb70')
    der = bytes.fromhex('3045022100dc92655fe37036f47756db8102e0d7d5e28b3beb83a8fef4f5dc0559bddfb94e02205a36d4e4e6c7fcd16658c50783e00c341609977aed3ad00937bf4ee942a89937')
    point = S256Point.parse(sec)
    sig = Signature.parse(der)
    print(point.verify(z, sig))

    hex_tx = '0100000001868278ed6ddfb6c1ed3ad5f8181eb0c7a385aa0836f01d5e4789e6bd304d87221a000000db00483045022100dc92655fe37036f47756db8102e0d7d5e28b3beb83a8fef4f5dc0559bddfb94e02205a36d4e4e6c7fcd16658c50783e00c341609977aed3ad00937bf4ee942a8993701483045022100da6bee3c93766232079a01639d07fa869598749729ae323eab8eef53577d611b02207bef15429dcadce2121ea07f233115c6f09034c0be68db99980b9a6c5e75402201475221022626e955ea6ea6d98850c994f9107b036b1334f18ca8830bfff1295d21cfdb702103b287eaf122eea69030a0e9feed096bed8045c8b98bec453e1ffac7fbdbd4bb7152aeffffffff04d3b11400000000001976a914904a49878c0adfc3aa05de7afad2cc15f483a56a88ac7f400900000000001976a914418327e3f3dda4cf5b9089325a4b95abdfa0334088ac722c0c00000000001976a914ba35042cfe9fc66fd35ac2224eebdafd1028ad2788acdc4ace020000000017a91474d691da1574e6b3c192ecfb52cc8984ee7b6c568700000000'
    hex_sec = '03b287eaf122eea69030a0e9feed096bed8045c8b98bec453e1ffac7fbdbd4bb71'
    hex_der = '3045022100da6bee3c93766232079a01639d07fa869598749729ae323eab8eef53577d611b02207bef15429dcadce2121ea07f233115c6f09034c0be68db99980b9a6c5e754022'
    hex_redeem_script = '475221022626e955ea6ea6d98850c994f9107b036b1334f18ca8830bfff1295d21cfdb702103b287eaf122eea69030a0e9feed096bed8045c8b98bec453e1ffac7fbdbd4bb7152ae'
    sec = bytes.fromhex(hex_sec)
    der = bytes.fromhex(hex_der)
    redeem_script = Script.parse(BytesIO(bytes.fromhex(hex_redeem_script)))
    stream = BytesIO(bytes.fromhex(hex_tx))

# zmodyfikuj transakcję
    tx_obj = Tx.parse(stream)
# zacznij od wersji
    s = int_to_little_endian(tx_obj.version, 4)
# dodaj liczbę wejść
    s += encode_varint(len(tx_obj.tx_ins))
    i = tx_obj.tx_ins[0]
# zmodyfikuj pojedyncze TxIn tak, aby ScriptSig był skryptem RedeemScript
    s += TxIn(i.prev_tx, i.prev_index, redeem_script, i.sequence).serialize()
# dodaj liczbę wyjść
    s += encode_varint(len(tx_obj.tx_outs))
# dodaj serializację każdego wyjścia
    for tx_out in tx_obj.tx_outs:
        s += tx_out.serialize()
# dodaj czas blokady
    s += int_to_little_endian(tx_obj.locktime, 4)
# dodaj SIGHASH_ALL
    s += int_to_little_endian(SIGHASH_ALL, 4)
# oblicz skrót hash256 wyniku
# interpretuj go jako liczbę big-endian
    z = int.from_bytes(hash256(s), 'big')
# przeanalizuj S256Point#
    point = S256Point.parse(sec)
# przeanalizuj podpis
    sig = Signature.parse(der)
# sprawdź, czy punkt, z i podpis są poprawne
    print(point.verify(z, sig))

    print('Testy:')
    run_all(misc_tests.HelperTest)
    run_all(misc_tests.TxTest)
    run_all(misc_tests.OpTest)
    run_all(misc_tests.ScriptTest)

   
