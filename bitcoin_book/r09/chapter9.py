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
    # run_all(misc_tests.HelperTest)
    # run_all(misc_tests.TxTest)
    # run_all(misc_tests.OpTest)
    # run_all(misc_tests.ScriptTest)

    print('Rozdział 9')


   
