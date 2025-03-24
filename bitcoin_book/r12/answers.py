'''
# tag::exercise1[]
==== Ćwiczenie 1

Oblicz wynik filtra Blooma dla sekwencji `hello world` i `goodbye`, używając funkcji skrótu hash160 dla pola bitowego o długości 10.
# end::exercise1[]
# tag::answer1[]
>>> from helper import hash160
>>> bit_field_size = 10
>>> bit_field = [0] * bit_field_size
>>> for item in (b'hello world', b'goodbye'):
...     h = hash160(item)
...     bit = int.from_bytes(h, 'big') % bit_field_size
...     bit_field[bit] = 1
>>> print(bit_field)
[1, 1, 0, 0, 0, 0, 0, 0, 0, 0]

# end::answer1[]
# tag::exercise2[]
==== Ćwiczenie 2

Dla filtra Blooma o następujących parametrach: `size=10`, `function_count=5`, `tweak=99` określ, które bity zostaną ustawione po dodaniu tych elementów. (Użyj funkcji `bit_field_to_bytes` do konwersji na bajty).

* `b'Hello World'`
* `b'Goodbye!'`
# end::exercise2[]
# tag::answer2[]
>>> from bloomfilter import BloomFilter, BIP37_CONSTANT
>>> from helper import bit_field_to_bytes, murmur3
>>> field_size = 10
>>> function_count = 5
>>> tweak = 99
>>> items = (b'Hello World',  b'Goodbye!')
>>> bit_field_size = field_size * 8
>>> bit_field = [0] * bit_field_size
>>> for item in items:
...     for i in range(function_count):
...         seed = i * BIP37_CONSTANT + tweak
...         h = murmur3(item, seed=seed)
...         bit = h % bit_field_size
...         bit_field[bit] = 1
>>> print(bit_field_to_bytes(bit_field).hex())
4000600a080000010940

# end::answer2[]
# tag::exercise6[]
==== Ćwiczenie 6

Pobierz identyfikator bieżącego bloku w testnecie prześlij sobie kilka tBTC, znajdź UTXO odpowiadający tym tBTC bez użycia eksploratora bloków, utwórz transakcję, wykorzystując ten UTXO jako wejście, i wyślij komunikat `tx` w sieci testnet.
# end::exercise6[]
# tag::answer6[]
>>> import time
>>> from block import Block
>>> from bloomfilter import BloomFilter
>>> from ecc import PrivateKey
>>> from helper import (
...     decode_base58,
...     encode_varint,
...     hash256,
...     little_endian_to_int,
...     read_varint,
... )
>>> from merkleblock import MerkleBlock
>>> from network import (
...     GetDataMessage,
...     GetHeadersMessage,
...     HeadersMessage,
...     NetworkEnvelope,
...     SimpleNode,
...     TX_DATA_TYPE,
...     FILTERED_BLOCK_DATA_TYPE,
... )
>>> from script import p2pkh_script, Script
>>> from tx import Tx, TxIn, TxOut
>>> last_block_hex = '00000000000000a03f9432ac63813c6710bfe41712ac5ef6faab093f\
e2917636'
>>> secret = little_endian_to_int(hash256(b'Jimmy Song'))
>>> private_key = PrivateKey(secret=secret)
>>> addr = private_key.point.address(testnet=True)
>>> h160 = decode_base58(addr)
>>> target_address = 'mwJn1YPMq7y5F8J3LkC5Hxg9PHyZ5K4cFv'
>>> target_h160 = decode_base58(target_address)
>>> target_script = p2pkh_script(target_h160)
>>> fee = 5000  # fee in satoshis
>>> # Połącz się z testnet.programmingbitcoin.com w trybie testnet
>>> node = SimpleNode('testnet.programmingbitcoin.com', testnet=True, logging=\
False)
>>> # Utwórz filtr Blooma o rozmiarze 30 z 5 funkcjami, dodaj ulepszenie
>>> bf = BloomFilter(30, 5, 90210)
>>> # Dodaj h160 do filtra Blooma
>>> bf.add(h160)
>>> # Zakończ uzgadnianie
>>> node.handshake()
>>> # Załaduj filtr Blooma za pomocą polecenia filterload
>>> node.send(bf.filterload())
>>> # Ustaw blok początkowy na wartość last_block zdefiniowaną powyżej
>>> start_block = bytes.fromhex(last_block_hex)
>>> # Wyślij komunikat getheaders z blokiem początkowym
>>> getheaders = GetHeadersMessage(start_block=start_block)
>>> node.send(getheaders)
>>> # Czekaj na komunikat headers
>>> headers = node.wait_for(HeadersMessage)
>>> # Zapisz ostatni blok jako None
>>> last_block = None
>>> # Zainicjalizuj GetDataMessage
>>> getdata = GetDataMessage()
>>> # Przejdź pętlą przez bloki w nagłówkach
>>> for b in headers.blocks:
...      # Sprawdź, czy dowód pracy w bloku jest prawidłowy
...      if not b.check_pow():
...          raise RuntimeError('dowód pracy jest niepoprawny')
...      # Sprawdź, czy prev_block tego bloku jest ostatnim blokiem
...      if last_block is not None and b.prev_block != last_block:
...          raise RuntimeError('łańcuch przerwany')
...      # Dodaj nowy element do komunikatu getdata
...      # Powinny to być FILTERED_BLOCK_DATA_TYPE i skrót bloku
...      getdata.add_data(FILTERED_BLOCK_DATA_TYPE, b.hash())
...      # Ustaw ostatni blok na bieżący skrót
...      last_block = b.hash()
>>> # Wyślij komunikat getdata
>>> node.send(getdata)
>>> # Zainicjalizuj prev_tx, prev_index i prev_amount wartością None
>>> prev_tx, prev_index, prev_amount = None, None, None
>>> # Wykonuj pętlę, jeśli prev_tx ma wartość None
>>> while prev_tx is None:
...      # Czekaj na merkleblock lub tx
...      message = node.wait_for(MerkleBlock, Tx)
...      # Jeśli mamy komunikat merkleblock,
...      if message.command == b'merkleblock':
...          # to sprawdź, czy MerkleBlock jest poprawny,
...          if not message.is_valid():
...              raise RuntimeError('nieprawidłowy dowód drz. skrótów')
...      # w przeciwnym wypadku mamy komunikat tx
...      else:
...          # Ustaw warość True dla transakcji testnet
...          message.testnet = True
...          # Pętla po wszystkich wyjściach tx
...          for i, tx_out in enumerate(message.tx_outs):
...              # Jeśli wyjście ma ten sam adres co nasz adres, znaleźliśmy je
...              if tx_out.script_pubkey.address(testnet=True) == addr:
...                  # Znaleźliśmy utxo; przypisz wartości do prev_tx, prev_index i tx
...                  prev_tx = message.hash()
...                  prev_index = i
...                  prev_amount = tx_out.amount
...                  print('znaleziono: {}:{}'.format(prev_tx.hex(), prev_index))
found: b2cddd41d18d00910f88c31aa58c6816a190b8fc30fe7c665e1cd2ec60efdf3f:7
>>> # Utwórz TxIn
>>> tx_in = TxIn(prev_tx, prev_index)
>>> # Oblicz kwotę wyjścia (poprzednia kwota minus opłata)
>>> output_amount = prev_amount - fee
>>> # Utwórz nowe wyjście TxOut ze skryptem i z kwotą wyjścia
>>> tx_out = TxOut(output_amount, target_script)
>>> # Utwórz nową transakcję z jednym wejściem i z jednym wyjściem
>>> tx_obj = Tx(1, [tx_in], [tx_out], 0, testnet=True)
>>> # Podpisz jedyne wejście transakcji
>>> print(tx_obj.sign_input(0, private_key))
True
>>> # Serializuj i zamień na hex, aby zobaczyć, jak to wygląda
>>> print(tx_obj.serialize().hex())
01000000013fdfef60ecd21c5e667cfe30fcb890a116688ca51ac3880f91008dd141ddcdb20700\
00006b483045022100ff77d2559261df5490ed00d231099c4b8ea867e6ccfe8e3e6d077313ed4f\
1428022033a1db8d69eb0dc376f89684d1ed1be75719888090388a16f1e8eedeb8067768012103\
dc585d46cfca73f3a75ba1ef0c5756a21c1924587480700c6eb64e3f75d22083ffffffff019334\
e500000000001976a914ad346f8eb57dee9a37981716e498120ae80e44f788ac00000000
>>> # Wyślij tę podpisaną transakcję do sieci
>>> node.send(tx_obj)
>>> # Poczekaj sekundę, aż transakcja dotrze, używając time.sleep(1)
>>> time.sleep(1)
>>> # Potem zapytaj drugi węzeł o tę transakcję
>>> # Utwórz GetDataMessage
>>> getdata = GetDataMessage()
>>> # Zapytaj o naszą transakcję, dodając ją do komunikatu
>>> getdata.add_data(TX_DATA_TYPE, tx_obj.hash())
>>> # Wyślij komunikat 
>>> node.send(getdata)
>>> # Teraz poczekaj na odpowiedź Tx
>>> received_tx = node.wait_for(Tx)
>>> # Jeśli otrzymana tx ma ten sam identyfikator co nasza tx, skończyliśmy!
>>> if received_tx.id() == tx_obj.id():
...     print('sukces!')
sukces!


# end::answer6[]
'''


from unittest import TestCase

from bloomfilter import BloomFilter, BIP37_CONSTANT
from helper import (
    encode_varint,
    int_to_little_endian,
    murmur3,
)
from network import (
    GenericMessage,
    GetDataMessage,
)


'''
# tag::exercise3[]
==== Ćwiczenie 3

Napisz metodę `add` dla klasy `BloomFilter`.
# end::exercise3[]
'''


# tag::answer3[]
def add(self, item):
    for i in range(self.function_count):
        seed = i * BIP37_CONSTANT + self.tweak
        h = murmur3(item, seed=seed)
        bit = h % (self.size * 8)
        self.bit_field[bit] = 1
# end::answer3[]


'''
# tag::exercise4[]
==== Ćwiczenie 4

Napisz metodę `filterload` dla klasy `BloomFilter`.
# end::exercise4[]
'''


# tag::answer4[]
def filterload(self, flag=1):
    payload = encode_varint(self.size)
    payload += self.filter_bytes()
    payload += int_to_little_endian(self.function_count, 4)
    payload += int_to_little_endian(self.tweak, 4)
    payload += int_to_little_endian(flag, 1)
    return GenericMessage(b'filterload', payload)
# end::answer4[]


'''
# tag::exercise5[]
==== Ćwiczenie 5

Napisz metodę `serialize` dla klasy `GetDataMessage`.
# end::exercise5[]
'''


# tag::answer5[]
def serialize(self):
    result = encode_varint(len(self.data))
    for data_type, identifier in self.data:
        result += int_to_little_endian(data_type, 4)
        result += identifier[::-1]
    return result
# end::answer5[]


class ChapterTest(TestCase):

    def test_apply(self):
        BloomFilter.add = add
        BloomFilter.filterload = filterload
        GetDataMessage.serialize = serialize
