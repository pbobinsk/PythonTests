from io import BytesIO
from logging import getLogger

import json
import requests

from bitcoin_module.helper import (
    encode_varint,
    hash256,
    int_to_little_endian,
    little_endian_to_int,
    read_varint,
    SIGHASH_ALL
)
from bitcoin_module.script import Script

LOGGER = getLogger(__name__)


# tag::source7[]
class TxFetcher:
    cache = {}

    @classmethod
    def get_url(cls, testnet=False):
        if testnet:
            return 'https://blockstream.info/testnet/api/'
        else:
            return 'https://blockstream.info/api/'

    @classmethod
    def fetch(cls, tx_id, testnet=False, fresh=False):
        if fresh or (tx_id not in cls.cache):
            url = '{}/tx/{}/hex'.format(cls.get_url(testnet), tx_id)
            response = requests.get(url)
            LOGGER.info('fetching '+url)
            try:
                raw = bytes.fromhex(response.text.strip())
            except ValueError:
                raise ValueError('unexpected response: {}'.format(response.text))
            if raw[4] == 0:
                raw = raw[:4] + raw[6:]
                tx = Tx.parse(BytesIO(raw), testnet=testnet)
                tx.locktime = little_endian_to_int(raw[-4:])
            else:
                tx = Tx.parse(BytesIO(raw), testnet=testnet)
            if tx.id() != tx_id:  # <1>
                raise ValueError('not the same id: {} vs {}'.format(tx.id(), 
                                  tx_id))
            cls.cache[tx_id] = tx
        cls.cache[tx_id].testnet = testnet
        return cls.cache[tx_id]
    # end::source7[]

    @classmethod
    def get_hex(cls, tx_id, testnet=False, fresh=False):
        url = '{}/tx/{}/hex'.format(cls.get_url(testnet), tx_id)
        response = requests.get(url)
        try:
            raw = response.text.strip()
        except ValueError:
            raise ValueError('unexpected response: {}'.format(response.text))
        return raw


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
        num_outputs = read_varint(s)
        outputs = []
        for _ in range(num_outputs):
            outputs.append(TxOut.parse(s))
        locktime = little_endian_to_int(s.read(4))
        return cls(version, inputs, outputs, locktime, testnet=testnet)


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

    def fee(self, testnet=False):
        '''Zwraca opłatę dla tej transakcji w satoshi'''
        input_sum, output_sum, i = 0, 0, 0
        LOGGER.info('fee start')
        for tx_in in self.tx_ins:
            LOGGER.info(i)
            i += 1 
            input_sum += tx_in.value(testnet=testnet)
        for tx_out in self.tx_outs:
            output_sum += tx_out.amount
        LOGGER.info(f'inputs {input_sum} outputs {output_sum}')
        return input_sum - output_sum

    def sig_hash(self, input_index):
        '''Zwraca liczbę całkowitą będącą skrótem, który musi zostać
        podpisany dla indeksu input_index'''
        # rozpocznij serializację od wersji
        # użyj int_to_little_endian na 4 bajtach
        # dodaj liczbę wejść, używając encode_varint
        # wykonaj pętlę dla każdego wejścia, używając wyliczenia, aby otrzymać indeks wejścia
            # jeśli indeks wejścia jest tym, które podpisujemy,
            # ScriptSig-iem jest ScriptPubkey poprzedniej tx;
            # w przeciwnym razie ScriptSig jest pusty
            # dodaj serializację wejścia przy użyciu ScriptSig
        # dodaj liczbę wyjść, używając encode_varint
        # dodaj serializację każdego wyjścia
        # dodaj czas blokady, używając int_to_little_endian na 4 bajtach
        # dodaj SIGHASH_ALL, używając int_to_little_endian na 4 bajtach
        # serializacja hash256 
        # skonwertuj wynik na liczbę całkowitą za pomocą int.from_bytes (x, 'big')
        s = int_to_little_endian(self.version, 4)
        s += encode_varint(len(self.tx_ins))
        for i, tx_in in enumerate(self.tx_ins):
            if i == input_index:
                s += TxIn(
                    prev_tx=tx_in.prev_tx,
                    prev_index=tx_in.prev_index,
                    script_sig=tx_in.script_pubkey(self.testnet),
                    sequence=tx_in.sequence,
                ).serialize()
            else:
                s += TxIn(
                    prev_tx=tx_in.prev_tx,
                    prev_index=tx_in.prev_index,
                    sequence=tx_in.sequence,
                ).serialize()
        s += encode_varint(len(self.tx_outs))
        for tx_out in self.tx_outs:
            s += tx_out.serialize()
        s += int_to_little_endian(self.locktime, 4)
        s += int_to_little_endian(SIGHASH_ALL, 4)
        h256 = hash256(s)
        return int.from_bytes(h256, 'big')

    def verify_input(self, input_index):
        '''Określa, czy wejście ma prawidłowy podpis'''
        # weź odpowiednie wejście
        # weź poprzedni ScriptPubKey
        # weź skrót podpisu (z)
        # połącz bieżący ScriptSig z poprzednim ScriptPubKey
        # zinterpretuj scalony skrypt
        tx_in = self.tx_ins[input_index]
        script_pubkey = tx_in.script_pubkey(testnet=self.testnet)
        z = self.sig_hash(input_index)
        combined = tx_in.script_sig + script_pubkey
        return combined.evaluate(z)

    # tag::source2[]
    def verify(self):
        '''Zweryfikuj tę transakcję'''
        LOGGER.info(f'inputs: {len(self.tx_ins)}')
        if self.fee() < 0:  # <1>
            return False
        LOGGER.info('verify')
        for i in range(len(self.tx_ins)):
            LOGGER.info(i)
            if not self.verify_input(i):  # <2>
                return False
        return True
    # end::source2[]

    def sign_input(self, input_index, private_key):
        # weź skrót podpisu (z)
        # utwórz podpis DER skrótu, używając klucza prywatnego
        # dołącz SIGHASH_ALL do DER (użyj SIGHASH_ALL.to_bytes (1, 'big'))
        # oblicz SEC
        # zainicjuj nowy skrypt, używając [sig, sec] jako poleceń
        # zmień input_script_sig na nowy skrypt
        # zwróć prawdę, jeśli podpis sig jest poprawny, używając self.verify_input
        z = self.sig_hash(input_index)
        der = private_key.sign(z).der()
        sig = der + SIGHASH_ALL.to_bytes(1, 'big')
        sec = private_key.point.sec()
        self.tx_ins[input_index].script_sig = Script([sig, sec])
        return self.verify_input(input_index)


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
        amount = little_endian_to_int(s.read(8))
        script_pubkey = Script.parse(s)
        return cls(amount, script_pubkey)

    # tag::source4[]
    def serialize(self):  # <1>
        '''Zwraca bajtową serializację wyjścia transakcji'''
        result = int_to_little_endian(self.amount, 8)
        result += self.script_pubkey.serialize()
        return result
    # end::source4[]


