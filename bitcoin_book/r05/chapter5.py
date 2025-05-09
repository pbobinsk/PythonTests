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

    run(misc_tests.TxTest("test_parse_version"))

    print('Script from hex')
    script_hex = ('6b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278a')
    stream = BytesIO(bytes.fromhex(script_hex))
    script_sig = Script.parse(stream)
    print(script_sig)

    cache_file = './tx.cache'
    fetched_tx_1 = TxFetcher.fetch('4254b23e407dcdbebb50f0f1282fd5efe509e9cf0392a3882fe046822b08be90')
    fetched_tx_2 = TxFetcher.fetch('55264f4d072df872a3d48038cd5dd4885565c0cc3d25577c4492785899a901d2')
    fetched_tx_3 = TxFetcher.fetch('df84650a6301418de871052350513695f881c9713f75ae516c6881fb2ad9dd4d')
    TxFetcher.dump_cache(cache_file)

    run(misc_tests.TxTest("test_parse_inputs"))

    run(misc_tests.TxTest("test_parse_outputs"))

    run_all(misc_tests.TxTest)
    
    '''
    f4566ae9e668de340aab0f69d3c41c11ae85d3f45ced46a410917aec3ec44fc1	0.00020000 BTC	191 vB	9.0 sat/vB
    4254b23e407dcdbebb50f0f1282fd5efe509e9cf0392a3882fe046822b08be90	0.01918700 BTC	142 vB	5.5 sat/vB
    55264f4d072df872a3d48038cd5dd4885565c0cc3d25577c4492785899a901d2	0.01027432 BTC	345 vB	6.5 sat/vB
    df84650a6301418de871052350513695f881c9713f75ae516c6881fb2ad9dd4d	0.00391409 BTC	144 vB	5.9 sat/vB
    '''
    script_hex = '0200000001b4b31cadff9160af1a1fa2cdfe77ffeffbb0328c24833f545f07762e28e019fc000000006a47304402203345c2345832f2668ba0cc96072ea665da034b7df5b059668e6f974f9d794cca02207edea156d639d1c5b8c6f335ac704939dcc2894277eff4675313e5de912540b901210341f1625ebc90fa4ac5ae6ba29a98ab95af30e56d63a4e9b35cdb2de078ede276ffffffff0172470000000000001976a914ed990253368c1c871ddff7bb27dee32d4dbd296388ac00000000'
    example_tx = Tx.parse(BytesIO(bytes.fromhex(script_hex)))

    print(example_tx)

    fetched_hex = TxFetcher.get_hex('f4566ae9e668de340aab0f69d3c41c11ae85d3f45ced46a410917aec3ec44fc1')
    print(fetched_hex == script_hex)

    fetched_tx_1 = TxFetcher.fetch('4254b23e407dcdbebb50f0f1282fd5efe509e9cf0392a3882fe046822b08be90')
    print(fetched_tx_1)

    fetched_tx_2 = TxFetcher.fetch('55264f4d072df872a3d48038cd5dd4885565c0cc3d25577c4492785899a901d2')
    fetched_tx_3 = TxFetcher.fetch('df84650a6301418de871052350513695f881c9713f75ae516c6881fb2ad9dd4d')



    print(example_tx.fee())
    print(fetched_tx_1.fee())
    print(fetched_tx_2.fee())
    print(fetched_tx_3.fee())
    

