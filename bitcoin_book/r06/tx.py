from io import BytesIO
from unittest import TestCase

import json
import requests

from helper import (
    encode_varint,
    hash256,
    int_to_little_endian,
    little_endian_to_int,
    read_varint,
)
from script import Script


class TxFetcher:
    cache = {}

    @classmethod
    def get_url(cls, testnet=False):
        if testnet:
            return 'http://testnet.programmingbitcoin.com'
        else:
            return 'http://mainnet.programmingbitcoin.com'

    @classmethod
    def fetch(cls, tx_id, testnet=False, fresh=False):
        if fresh or (tx_id not in cls.cache):
            url = '{}/tx/{}.hex'.format(cls.get_url(testnet), tx_id)
            response = requests.get(url)
            try:
                raw = bytes.fromhex(response.text.strip())
            except ValueError:
                raise ValueError('nieoczekiwana odpowiedź: {}'.format(response.text))
            # upewnij się, że transakcja, którą mamy, odpowiada skrótowi, o który pytaliśmy
            if raw[4] == 0:
                raw = raw[:4] + raw[6:]
                tx = Tx.parse(BytesIO(raw), testnet=testnet)
                tx.locktime = little_endian_to_int(raw[-4:])
            else:
                tx = Tx.parse(BytesIO(raw), testnet=testnet)
            if tx.id() != tx_id:
                raise ValueError('różne identyfikatory: {} vs {}'.format(tx.id(), tx_id))
            cls.cache[tx_id] = tx
        cls.cache[tx_id].testnet = testnet
        return cls.cache[tx_id]

    @classmethod
    def load_cache(cls, filename):
        disk_cache = json.loads(open(filename, 'r').read())
        for k, raw_hex in disk_cache.items():
            raw = bytes.fromhex(raw_hex)
            if raw[4] == 0:
                raw = raw[:4] + raw[6:]
                tx = Tx.parse(BytesIO(raw))
                tx.locktime = little_endian_to_int(raw[-4:])
            else:
                tx = Tx.parse(BytesIO(raw))
            cls.cache[k] = tx

    @classmethod
    def dump_cache(cls, filename):
        with open(filename, 'w') as f:
            to_dump = {k: tx.serialize().hex() for k, tx in cls.cache.items()}
            s = json.dumps(to_dump, sort_keys=True, indent=4)
            f.write(s)


class Tx:

    def __init__(self, version, tx_ins, tx_outs, locktime, testnet=False):
        self.version = version
        self.tx_ins = tx_ins
        self.tx_outs = tx_outs
        self.locktime = locktime
        self.testnet = testnet

    def __repr__(self):
        tx_ins = ''
        for tx_in in self.tx_ins:
            tx_ins += tx_in.__repr__() + '\n'
        tx_outs = ''
        for tx_out in self.tx_outs:
            tx_outs += tx_out.__repr__() + '\n'
        return 'tx: {}\nversion: {}\ntx_ins:\n{}tx_outs:\n{}locktime: {}'.format(
            self.id(),
            self.version,
            tx_ins,
            tx_outs,
            self.locktime,
        )

    def id(self):
        '''Czytelna dla człowieka heksadecymalna postać skrótu transakcji'''
        return self.hash().hex()

    def hash(self):
        '''Binarny skrót w starej serializacji'''
        return hash256(self.serialize())[::-1]

    @classmethod
    def parse(cls, s, testnet=False):
        '''Przetwarza strumień bajtów i zwraca transakcję z jego początku;
        zwraca obiekt Tx
        '''
        # s.read (n) zwróci n bajtów
        # version jest 4-bajtową liczbą całkowitą w porządku little-endian
        version = little_endian_to_int(s.read(4))
        # num_inputs to zmienna varint; trzeba użyć read_varint(s)
        num_inputs = read_varint(s)
        # zinterpretować liczbę wejść transakcyjnych w num_inputs
        inputs = []
        for _ in range(num_inputs):
            inputs.append(TxIn.parse(s))
        # zamienić num_outputs na varint, użyć read_varint(s)
        num_outputs = read_varint(s)
        # zinterpretować liczbę wyjść transakcyjnych w num_outputs
        outputs = []
        for _ in range(num_outputs):
            outputs.append(TxOut.parse(s))
        # locktime jest 4-bajtową liczbą całkowitą w porządku little-endian
        locktime = little_endian_to_int(s.read(4))
        # zwraca instancję klasy (argumenty, zobacz w __init__)
        return cls(version, inputs, outputs, locktime, testnet=testnet)

    def serialize(self):
        '''Zwraca bajtową serializację transakcji'''
        # serializuj zmienną version (4 bajty, porządek little endian)
        result = int_to_little_endian(self.version, 4)
        # zakoduj liczbę wejść używając encode_varint
        result += encode_varint(len(self.tx_ins))
        # iteruj po wejściach
        for tx_in in self.tx_ins:
            # serializuj każde wejście
            result += tx_in.serialize()
        # zakoduj liczbę wyjść, używając encode_varint
        result += encode_varint(len(self.tx_outs))
        # iteruj po wyjściach
        for tx_out in self.tx_outs:
            # serializuj każde wyjście
            result += tx_out.serialize()
        # serializuj czas blokady (4 bajty, porządek little endian)
        result += int_to_little_endian(self.locktime, 4)
        return result

    def fee(self):
        '''Zwraca opłatę dla tej transakcji w satoshi'''
        # zainicjuj sumę wejść i sumę wyjść
        input_sum, output_sum = 0, 0
        # użyj TxIn.value (), aby zsumować kwoty z wejść
        for tx_in in self.tx_ins:
            input_sum += tx_in.value(self.testnet)
        # użyj TxOut.amount, aby zsumować kwoty z wyjść
        for tx_out in self.tx_outs:
            output_sum += tx_out.amount
        # fee (opłata) to suma wejść - suma wyjść
        return input_sum - output_sum


class TxIn:

    def __init__(self, prev_tx, prev_index, script_sig=None, sequence=0xffffffff):
        self.prev_tx = prev_tx
        self.prev_index = prev_index
        if script_sig is None:
            self.script_sig = Script()
        else:
            self.script_sig = script_sig
        self.sequence = sequence

    def __repr__(self):
        return '{}:{}'.format(
            self.prev_tx.hex(),
            self.prev_index,
        )

    @classmethod
    def parse(cls, s):
        '''Interpretuje tx_input na początku strumienia bajtów;
        zwraca obiekt TxIn
        '''
        # prev_tx ma długość 32 bajtów, porządek little endian
        prev_tx = s.read(32)[::-1]
        # prev_index jest 4-bajtową liczbą całkowitą w porządku little-endia
        prev_index = little_endian_to_int(s.read(4))
        # aby uzyskać ScriptSig, użyj Script.parse
        script_sig = Script.parse(s)
        # sequence jest 4-bajtową liczbą całkowitą w porządku little-endian
        sequence = little_endian_to_int(s.read(4))
        # zwraca instancję klasy (argumenty, zobacz w __init__)
        return cls(prev_tx, prev_index, script_sig, sequence)

    def serialize(self):
        '''Zwraca bajtową serializację wejścia transakcji'''
        # serializuj prev_tx, porządek little endian
        result = self.prev_tx[::-1]
        # serializuj prev_ inex (4 bajty, porządek little endian)
        result += int_to_little_endian(self.prev_index, 4)
        # serializuj script_sig
        result += self.script_sig.serialize()
        # serializuj nr porządkowy (4 bajty, porządek little endian)
        result += int_to_little_endian(self.sequence, 4)
        return result

    def fetch_tx(self, testnet=False):
        return TxFetcher.fetch(self.prev_tx.hex(), testnet=testnet)

    def value(self, testnet=False):
        '''Pobiera wartość wyjścia, sprawdzając skrót transakcji.
        Zwraca kwotę w jednostkach satoshi.
        '''
        # aby pobrać transakcję, użyj self.fetch_tx
        tx = self.fetch_tx(testnet=testnet)
        # pobierz wyjście o indeksie self.prev_index
        # zwróć właściwość amount
        return tx.tx_outs[self.prev_index].amount

    def script_pubkey(self, testnet=False):
        '''Pobiera pole ScriptPubKey, sprawdzając skrót transakcji.
        Zwraca obiekt Script.
        '''
        # aby pobrać transakcję, użyj self.fetch_tx
        tx = self.fetch_tx(testnet=testnet)
        # pobierz wyjście o indeksie self.prev_index
        # zwróć właściwość script_pubkey
        return tx.tx_outs[self.prev_index].script_pubkey


class TxOut:

    def __init__(self, amount, script_pubkey):
        self.amount = amount
        self.script_pubkey = script_pubkey

    def __repr__(self):
        return '{}:{}'.format(self.amount, self.script_pubkey)

    @classmethod
    def parse(cls, s):
        '''Interpretuje tx_output na początku strumienia bajtów;
        zwraca obiekt TxOut
        '''
        # kwota (amount) jest 8-bajtową liczbą całkowitą w porządku little-endian
        amount = little_endian_to_int(s.read(8))
        # aby uzyskać ScriptPubKey, użyj Script.parse
        script_pubkey = Script.parse(s)
        # zwraca instancję klasy (argumenty, zobacz w __init__)
        return cls(amount, script_pubkey)

    def serialize(self):
        '''Zwraca bajtową serializację wyjścia transakcji'''
        # serializuj kwotę (8 bajtów, porządek little endian)
        result = int_to_little_endian(self.amount, 8)
        # serializuj script_pubkey
        result += self.script_pubkey.serialize()
        return result


class TxTest(TestCase):
    cache_file = '../tx.cache'

    @classmethod
    def setUpClass(cls):
        # wstaw z cache, aby nie trzeba było być online, by uruchomić te testy
        TxFetcher.load_cache(cls.cache_file)

    def test_parse_version(self):
        raw_tx = bytes.fromhex('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(tx.version, 1)

    def test_parse_inputs(self):
        raw_tx = bytes.fromhex('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(len(tx.tx_ins), 1)
        want = bytes.fromhex('d1c789a9c60383bf715f3f6ad9d14b91fe55f3deb369fe5d9280cb1a01793f81')
        self.assertEqual(tx.tx_ins[0].prev_tx, want)
        self.assertEqual(tx.tx_ins[0].prev_index, 0)
        want = bytes.fromhex('6b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278a')
        self.assertEqual(tx.tx_ins[0].script_sig.serialize(), want)
        self.assertEqual(tx.tx_ins[0].sequence, 0xfffffffe)

    def test_parse_outputs(self):
        raw_tx = bytes.fromhex('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(len(tx.tx_outs), 2)
        want = 32454049
        self.assertEqual(tx.tx_outs[0].amount, want)
        want = bytes.fromhex('1976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac')
        self.assertEqual(tx.tx_outs[0].script_pubkey.serialize(), want)
        want = 10011545
        self.assertEqual(tx.tx_outs[1].amount, want)
        want = bytes.fromhex('1976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac')
        self.assertEqual(tx.tx_outs[1].script_pubkey.serialize(), want)

    def test_parse_locktime(self):
        raw_tx = bytes.fromhex('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(tx.locktime, 410393)

    def test_fee(self):
        raw_tx = bytes.fromhex('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(tx.fee(), 40000)
        raw_tx = bytes.fromhex('010000000456919960ac691763688d3d3bcea9ad6ecaf875df5339e148a1fc61c6ed7a069e010000006a47304402204585bcdef85e6b1c6af5c2669d4830ff86e42dd205c0e089bc2a821657e951c002201024a10366077f87d6bce1f7100ad8cfa8a064b39d4e8fe4ea13a7b71aa8180f012102f0da57e85eec2934a82a585ea337ce2f4998b50ae699dd79f5880e253dafafb7feffffffeb8f51f4038dc17e6313cf831d4f02281c2a468bde0fafd37f1bf882729e7fd3000000006a47304402207899531a52d59a6de200179928ca900254a36b8dff8bb75f5f5d71b1cdc26125022008b422690b8461cb52c3cc30330b23d574351872b7c361e9aae3649071c1a7160121035d5c93d9ac96881f19ba1f686f15f009ded7c62efe85a872e6a19b43c15a2937feffffff567bf40595119d1bb8a3037c356efd56170b64cbcc160fb028fa10704b45d775000000006a47304402204c7c7818424c7f7911da6cddc59655a70af1cb5eaf17c69dadbfc74ffa0b662f02207599e08bc8023693ad4e9527dc42c34210f7a7d1d1ddfc8492b654a11e7620a0012102158b46fbdff65d0172b7989aec8850aa0dae49abfb84c81ae6e5b251a58ace5cfeffffffd63a5e6c16e620f86f375925b21cabaf736c779f88fd04dcad51d26690f7f345010000006a47304402200633ea0d3314bea0d95b3cd8dadb2ef79ea8331ffe1e61f762c0f6daea0fabde022029f23b3e9c30f080446150b23852028751635dcee2be669c2a1686a4b5edf304012103ffd6f4a67e94aba353a00882e563ff2722eb4cff0ad6006e86ee20dfe7520d55feffffff0251430f00000000001976a914ab0c0b2e98b1ab6dbf67d4750b0a56244948a87988ac005a6202000000001976a9143c82d7df364eb6c75be8c80df2b3eda8db57397088ac46430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(tx.fee(), 140500)
