from io import BytesIO
from unittest import TestCase

import json
import requests

from bitcoin_module.helper import (
    encode_varint,
    hash256,
    int_to_little_endian,
    little_endian_to_int,
    read_varint,
)
from bitcoin_module.script import Script


# tag::source7[]
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
            if raw[4] == 0:
                raw = raw[:4] + raw[6:]
                tx = Tx.parse(BytesIO(raw), testnet=testnet)
                tx.locktime = little_endian_to_int(raw[-4:])
            else:
                tx = Tx.parse(BytesIO(raw), testnet=testnet)
            if tx.id() != tx_id:  # <1>
                raise ValueError('różne identyfikatory: {} vs {}'.format(tx.id(), 
                                  tx_id))
            cls.cache[tx_id] = tx
        cls.cache[tx_id].testnet = testnet
        return cls.cache[tx_id]
    # end::source7[]

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


# tag::source1[]
class Tx:

    def __init__(self, version, tx_ins, tx_outs, locktime, testnet=False):
        self.version = version
        self.tx_ins = tx_ins  # <1>
        self.tx_outs = tx_outs
        self.locktime = locktime
        self.testnet = testnet  # <2>

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

    def id(self):  # <3>
        '''Czytelna dla człowieka heksadecymalna postać skrótu transakcji'''
        return self.hash().hex()

    def hash(self):  # <4>
        '''Binarny skrót w starej serializacji'''
        return hash256(self.serialize())[::-1]
    # end::source1[]

    @classmethod
    def parse(cls, s, testnet=False):
        '''Przetwarza strumień bajtów i zwraca transakcję z jego początku;
        zwraca obiekt Tx
        '''
        # s.read (n) zwróci n bajtów
        # version jest 4-bajtową liczbą całkowitą w porządku little-endian
        # num_inputs to zmienna varint; trzeba użyć read_varint(s)
        # zinterpretować liczbę wejść transakcyjnych w num_inputs
        # zamienić num_outputs na varint, użyć read_varint(s)
        # zinterpretować liczbę wyjść transakcyjnych w num_outputs
        # locktime jest 4-bajtową liczbą całkowitą w porządku little-endian
        # zwraca instancję klasy (argumenty, zobacz w __init__)
        version = little_endian_to_int(s.read(4))

        num_inputs = read_varint(s)
        inputs = []
        for _ in range(num_inputs):
            inputs.append(TxIn.parse(s))
        return cls(version, inputs, None, None, testnet=testnet)


    # tag::source6[]
    def serialize(self):
        '''Zwraca bajtową serializację transakcji'''
        result = int_to_little_endian(self.version, 4)
        result += encode_varint(len(self.tx_ins))
        for tx_in in self.tx_ins:
            result += tx_in.serialize()
        result += encode_varint(len(self.tx_outs))
        for tx_out in self.tx_outs:
            result += tx_out.serialize()
        result += int_to_little_endian(self.locktime, 4)
        return result
    # end::source6[]

    def fee(self):
        '''Zwraca opłatę dla tej transakcji w satoshi'''
        # zainicjuj sumę wejść i sumę wyjść
        # użyj TxIn.value (), aby zsumować kwoty z wejść
        # użyj TxOut.amount, aby zsumować kwoty z wyjść
        # fee (opłata) to suma wejść - suma wyjść
        raise NotImplementedError


# tag::source2[]
class TxIn:
    def __init__(self, prev_tx, prev_index, script_sig=None, sequence=0xffffffff):
        self.prev_tx = prev_tx
        self.prev_index = prev_index
        if script_sig is None:  # <1>
            self.script_sig = Script()
        else:
            self.script_sig = script_sig
        self.sequence = sequence

    def __repr__(self):
        return '{}:{}'.format(
            self.prev_tx.hex(),
            self.prev_index,
        )
    # end::source2[]

    @classmethod
    def parse(cls, s):
        '''Interpretuje tx_input na początku strumienia bajtów;
        zwraca obiekt TxIn
        '''
        # prev_tx ma długość 32 bajtów, porządek little endian
        # prev_index jest 4-bajtową liczbą całkowitą w porządku little-endian
        # aby uzyskać ScriptSig, użyj Script.parse
        # sequence jest 4-bajtową liczbą całkowitą w porządku little-endian
        # zwraca instancję klasy (argumenty, zobacz w __init__)
        prev_tx = s.read(32)[::-1]
        prev_index = little_endian_to_int(s.read(4))
        script_sig = Script.parse(s)
        sequence = little_endian_to_int(s.read(4))
        return cls(prev_tx, prev_index, script_sig, sequence)

    # tag::source5[]
    def serialize(self):
        '''Zwraca bajtową serializację wejścia transakcji'''
        result = self.prev_tx[::-1]
        result += int_to_little_endian(self.prev_index, 4)
        result += self.script_sig.serialize()
        result += int_to_little_endian(self.sequence, 4)
        return result
    # end::source5[]

    # tag::source8[]
    def fetch_tx(self, testnet=False):
        return TxFetcher.fetch(self.prev_tx.hex(), testnet=testnet)

    def value(self, testnet=False):
        '''Pobiera wartość wyjścia, sprawdzając skrót transakcji.
        Zwraca kwotę w jednostkach satoshi.
        '''
        tx = self.fetch_tx(testnet=testnet)
        return tx.tx_outs[self.prev_index].amount

    def script_pubkey(self, testnet=False):
        '''Pobiera pole ScriptPubKey, sprawdzając skrót transakcji.
        Zwraca obiekt Script.
        '''
        tx = self.fetch_tx(testnet=testnet)
        return tx.tx_outs[self.prev_index].script_pubkey
    # end::source8[]


# tag::source3[]
class TxOut:

    def __init__(self, amount, script_pubkey):
        self.amount = amount
        self.script_pubkey = script_pubkey

    def __repr__(self):
        return '{}:{}'.format(self.amount, self.script_pubkey)
    # end::source3[]

    @classmethod
    def parse(cls, s):
        '''Interpretuje tx_output na początku strumienia bajtów;
        zwraca obiekt TxOut
        '''
        # kwota (amount) jest 8-bajtową liczbą całkowitą w porządku little-endian
        # aby uzyskać ScriptPubKey, użyj Script.parse
        # zwraca instancję klasy (argumenty, zobacz w __init__)
        raise NotImplementedError

    # tag::source4[]
    def serialize(self):  # <1>
        '''Zwraca bajtową serializację wyjścia transakcji'''
        result = int_to_little_endian(self.amount, 8)
        result += self.script_pubkey.serialize()
        return result
    # end::source4[]


