import os, sys
from io import BytesIO
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../bitcoin_book")))
from bitcoin_module.tx import TxFetcher


if __name__ == "__main__":
    
    cache_file = './tx.cache'
    fetched_tx_1 = TxFetcher.fetch('4254b23e407dcdbebb50f0f1282fd5efe509e9cf0392a3882fe046822b08be90')
    fetched_tx_2 = TxFetcher.fetch('55264f4d072df872a3d48038cd5dd4885565c0cc3d25577c4492785899a901d2')
    fetched_tx_3 = TxFetcher.fetch('df84650a6301418de871052350513695f881c9713f75ae516c6881fb2ad9dd4d')
    fetched_tx_4 = TxFetcher.fetch('f4566ae9e668de340aab0f69d3c41c11ae85d3f45ced46a410917aec3ec44fc1')
    TxFetcher.dump_cache(cache_file)


    print('Transakcja 1')
    print(fetched_tx_1)
    print(f'Fee: {fetched_tx_1.fee()}')
    print('Transakcja 2')
    print(fetched_tx_2)
    print(f'Fee: {fetched_tx_2.fee()}')

