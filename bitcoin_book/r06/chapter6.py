import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bitcoin_module.helper import run, run_all, hash256, little_endian_to_int
import bitcoin_module.ecc_tests as ecc_tests
import bitcoin_module.misc_tests as misc_tests
from bitcoin_module.ecc import PrivateKey, PublicKey
import hashlib

from io import BytesIO
from bitcoin_module.script import Script
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

    # run_all(misc_tests.OpTest)
    # run_all(misc_tests.ScriptTest)
