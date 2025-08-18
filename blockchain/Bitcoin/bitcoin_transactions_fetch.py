import os, sys
from io import BytesIO
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../bitcoin_book")))
from bitcoin_module.tx import Tx, TxFetcher

if __name__ == "__main__":
    
    cache_file = './tx.cache'
    fetched_tx_1 = TxFetcher.fetch('4254b23e407dcdbebb50f0f1282fd5efe509e9cf0392a3882fe046822b08be90')
    fetched_tx_2 = TxFetcher.fetch('55264f4d072df872a3d48038cd5dd4885565c0cc3d25577c4492785899a901d2')
    fetched_tx_3 = TxFetcher.fetch('df84650a6301418de871052350513695f881c9713f75ae516c6881fb2ad9dd4d')
    TxFetcher.dump_cache(cache_file)

    '''
    f4566ae9e668de340aab0f69d3c41c11ae85d3f45ced46a410917aec3ec44fc1	0.00020000 BTC	191 vB	9.0 sat/vB
    4254b23e407dcdbebb50f0f1282fd5efe509e9cf0392a3882fe046822b08be90	0.01918700 BTC	142 vB	5.5 sat/vB
    55264f4d072df872a3d48038cd5dd4885565c0cc3d25577c4492785899a901d2	0.01027432 BTC	345 vB	6.5 sat/vB
    df84650a6301418de871052350513695f881c9713f75ae516c6881fb2ad9dd4d	0.00391409 BTC	144 vB	5.9 sat/vB
    '''
    script_hex = '0200000001b4b31cadff9160af1a1fa2cdfe77ffeffbb0328c24833f545f0776\
2e28e019fc000000006a47304402203345c2345832f2668ba0cc96072ea665da034b7df5b0\
59668e6f974f9d794cca02207edea156d639d1c5b8c6f335ac704939dcc2894277eff46753\
13e5de912540b901210341f1625ebc90fa4ac5ae6ba29a98ab95af30e56d63a4e9b35cdb2d\
e078ede276ffffffff0172470000000000001976a914ed990253368c1c871ddff7bb27dee3\
2d4dbd296388ac00000000'
    example_tx = Tx.parse(BytesIO(bytes.fromhex(script_hex)))

    print(f'Transakcja z hex={script_hex}')
    print(example_tx)

    id2fetch='f4566ae9e668de340aab0f69d3c41c11ae85d3f45ced46a410917aec3ec44fc1'
    fetched_hex = TxFetcher.get_hex(id2fetch)
    print(f'Ta sama transakcja z łańcucha po id={id2fetch}')
    print('Równe? ',fetched_hex == script_hex)

    
    print('Inne transakcje pobrane')
    fetched_tx_1 = TxFetcher.fetch('4254b23e407dcdbebb50f0f1282fd5efe509e9cf0392a3882fe046822b08be90')
    fetched_tx_2 = TxFetcher.fetch('55264f4d072df872a3d48038cd5dd4885565c0cc3d25577c4492785899a901d2')
    fetched_tx_3 = TxFetcher.fetch('df84650a6301418de871052350513695f881c9713f75ae516c6881fb2ad9dd4d')



    print(fetched_tx_1.id())
    print(f'Fee={fetched_tx_1.fee()}')
    print(fetched_tx_2.id())
    print(f'Fee={fetched_tx_2.fee()}')
    print(fetched_tx_3.id())
    print(f'Fee={fetched_tx_3.fee()}')
    

