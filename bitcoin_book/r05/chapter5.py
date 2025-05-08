import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bitcoin_module.helper import run, run_all, hash256, little_endian_to_int
import bitcoin_module.ecc_tests as ecc_tests
import bitcoin_module.misc_tests as misc_tests
from bitcoin_module.ecc import PrivateKey, PublicKey
import hashlib

from io import BytesIO
from bitcoin_module.script import Script

if __name__ == "__main__":
    
    print('Testy z poprzednich rozdziałów')
    run_all(ecc_tests.ECCTest)
    run_all(ecc_tests.S256Test)
    run_all(ecc_tests.PrivateKeyTest)
    run_all(ecc_tests.SignatureTest)
    run_all(misc_tests.HelperTest)

    run(misc_tests.TxTest("test_parse_version"))

    print('Script from hex')
    script_hex = ('6b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278a')
    stream = BytesIO(bytes.fromhex(script_hex))
    script_sig = Script.parse(stream)
    print(script_sig)


    run(misc_tests.TxTest("test_parse_inputs"))
    


