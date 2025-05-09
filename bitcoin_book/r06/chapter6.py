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

if __name__ == "__main__":
    
    print('Testy z poprzednich rozdziałów')
    run_all(ecc_tests.ECCTest)
    run_all(ecc_tests.S256Test)
    run_all(ecc_tests.PrivateKeyTest)
    run_all(ecc_tests.SignatureTest)
    run_all(misc_tests.HelperTest)
    run_all(misc_tests.TxTest)
    
