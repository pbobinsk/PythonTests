import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bitcoin_module.helper import run, run_all, hash256, little_endian_to_int
import bitcoin_module.ecc_tests as ecc_tests
import bitcoin_module.misc_tests as misc_tests
from bitcoin_module.ecc import PrivateKey, PublicKey
import hashlib

from io import BytesIO
from bitcoin_module.script import Script, LOGGER
from bitcoin_module.tx import *
import logging

if __name__ == "__main__":
    
    logging.basicConfig(level=logging.INFO)

    print('Testy z poprzednich rozdziałów')
    run_all(ecc_tests.ECCTest)
    run_all(ecc_tests.S256Test)
    run_all(ecc_tests.PrivateKeyTest)
    run_all(ecc_tests.SignatureTest)
    run_all(misc_tests.HelperTest)
    run_all(misc_tests.TxTest)
    

    print('Chapter 6')

    run(misc_tests.OpTest('test_op_hash160'))
    run(misc_tests.OpTest('test_op_checksig'))


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
    print(s)

    c1 = '255044462d312e330a25e2e3cfd30a0a0a312030206f626a0a3c3c2f57696474682032203020522f4865696768742033203020522f547970652034203020522f537562747970652035203020522f46696c7465722036203020522f436f6c6f7253706163652037203020522f4c656e6774682038203020522f42697473506572436f6d706f6e656e7420383e3e0a73747265616d0affd8fffe00245348412d3120697320646561642121212121852fec092339759c39b1a1c63c4c97e1fffe017f46dc93a6b67e013b029aaa1db2560b45ca67d688c7f84b8c4c791fe02b3df614f86db1690901c56b45c1530afedfb76038e972722fe7ad728f0e4904e046c230570fe9d41398abe12ef5bc942be33542a4802d98b5d70f2a332ec37fac3514e74ddc0f2cc1a874cd0c78305a21566461309789606bd0bf3f98cda8044629a1'
    c2 = '255044462d312e330a25e2e3cfd30a0a0a312030206f626a0a3c3c2f57696474682032203020522f4865696768742033203020522f547970652034203020522f537562747970652035203020522f46696c7465722036203020522f436f6c6f7253706163652037203020522f4c656e6774682038203020522f42697473506572436f6d706f6e656e7420383e3e0a73747265616d0affd8fffe00245348412d3120697320646561642121212121852fec092339759c39b1a1c63c4c97e1fffe017346dc9166b67e118f029ab621b2560ff9ca67cca8c7f85ba84c79030c2b3de218f86db3a90901d5df45c14f26fedfb3dc38e96ac22fe7bd728f0e45bce046d23c570feb141398bb552ef5a0a82be331fea48037b8b5d71f0e332edf93ac3500eb4ddc0decc1a864790c782c76215660dd309791d06bd0af3f98cda4bc4629b1'

    collision1 = bytes.fromhex(c1)  # <1>
    collision2 = bytes.fromhex(c2)
    script_sig = Script([collision1, collision2])
    combined_script = script_sig + s
    LOGGER.setLevel(logging.WARNING)
    print(combined_script.evaluate(0))

    run_all(misc_tests.OpTest)
    run_all(misc_tests.ScriptTest)
