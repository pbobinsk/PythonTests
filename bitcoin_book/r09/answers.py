'''
# tag::exercise12[]
==== Ćwiczenie 12

Oblicz reprezentację bitową, mając dany pierwszy i ostatni blok z tego 2016-blokowego okresu dopasowania trudności:

* Blok 471744:
+
```
000000203471101bbda3fe307664b3283a9ef0e97d9a38a7eacd88000000000000000000
10c8aba8479bbaa5e0848152fd3c2289ca50e1c3e58c9a4faaafbdf5803c5448ddb84559
7e8b0118e43a81d3
```

* Blok 473759:
+
```
02000020f1472d9db4b563c35f97c428ac903f23b7fc055d1cfc26000000000000000000
b3f449fcbe1bc4cfbcb8283a0d2c037f961a3fdf2b8bedc144973735eea707e126425859
7e8b0118e5f00474
```
# end::exercise12[]
# tag::answer12[]
>>> from io import BytesIO
>>> from block import Block
>>> from helper import TWO_WEEKS
>>> from helper import target_to_bits
>>> block1_hex = '000000203471101bbda3fe307664b3283a9ef0e97d9a38a7eacd88000000\
00000000000010c8aba8479bbaa5e0848152fd3c2289ca50e1c3e58c9a4faaafbdf5803c5448dd\
b845597e8b0118e43a81d3'
>>> block2_hex = '02000020f1472d9db4b563c35f97c428ac903f23b7fc055d1cfc26000000\
000000000000b3f449fcbe1bc4cfbcb8283a0d2c037f961a3fdf2b8bedc144973735eea707e126\
4258597e8b0118e5f00474'
>>> last_block = Block.parse(BytesIO(bytes.fromhex(block1_hex)))
>>> first_block = Block.parse(BytesIO(bytes.fromhex(block2_hex)))
>>> time_differential = last_block.timestamp - first_block.timestamp
>>> if time_differential > TWO_WEEKS * 4:
...     time_differential = TWO_WEEKS * 4
>>> if time_differential < TWO_WEEKS // 4:
...     time_differential = TWO_WEEKS // 4
>>> new_target = last_block.target() * time_differential // TWO_WEEKS
>>> new_bits = target_to_bits(new_target)
>>> print(new_bits.hex())
80df6217

# end::answer12[]
'''


from unittest import TestCase

import helper

from block import Block
from helper import (
    hash256,
    int_to_little_endian,
    little_endian_to_int,
    target_to_bits,
    TWO_WEEKS,
)
from tx import Tx


'''
# tag::exercise1[]
==== Ćwiczenie 1

Napisz metodę `is_coinbase` dla klasy `Tx`, sprawdzającą, czy dana transakcja jest transakcją coinbase.
# end::exercise1[]
'''


# tag::answer1[]
def is_coinbase(self):
    if len(self.tx_ins) != 1:
        return False
    first_input = self.tx_ins[0]
    if first_input.prev_tx != b'\x00' * 32:
        return False
    if first_input.prev_index != 0xffffffff:
        return False
    return True
# end::answer1[]


'''
# tag::exercise2[]
==== Ćwiczenie 2

Napisz metodę `coinbase_height` dla klasy `Tx`.
# end::exercise2[]
'''


# tag::answer2[]
def coinbase_height(self):
    if not self.is_coinbase():
        return None
    element = self.tx_ins[0].script_sig.cmds[0]
    return little_endian_to_int(element)
# end::answer2[]


'''
# tag::exercise3[]
==== Ćwiczenie 3

Napisz metodę `parse` dla klasy `Block`.
# end::exercise3[]
'''


# tag::answer3[]
@classmethod
def parse(cls, s):
    version = little_endian_to_int(s.read(4))
    prev_block = s.read(32)[::-1]
    merkle_root = s.read(32)[::-1]
    timestamp = little_endian_to_int(s.read(4))
    bits = s.read(4)
    nonce = s.read(4)
    return cls(version, prev_block, merkle_root, timestamp, bits, nonce)
# end::answer3[]


'''
# tag::exercise4[]
==== Ćwiczenie 4

Napisz metodę `serialize` dla klasy `Block`.
# end::exercise4[]
'''


# tag::answer4[]
def serialize(self):
    result = int_to_little_endian(self.version, 4)
    result += self.prev_block[::-1]
    result += self.merkle_root[::-1]
    result += int_to_little_endian(self.timestamp, 4)
    result += self.bits
    result += self.nonce
    return result
# end::answer4[]


'''
# tag::exercise5[]
==== Ćwiczenie 5

Napisz metodę `hash` dla klasy `Block`.
# end::exercise5[]
'''


# tag::answer5[]
def hash(self):
    s = self.serialize()
    sha = hash256(s)
    return sha[::-1]
# end::answer5[]


'''
# tag::exercise6[]
==== Ćwiczenie 6

Napisz metodę `bip9` dla klasy `Block`.
# end::exercise6[]
'''


# tag::answer6[]
def bip9(self):
    return self.version >> 29 == 0b001
# end::answer6[]


'''
# tag::exercise7[]
==== Ćwiczenie 7

Napisz metodę `bip91` dla klasy `Block`.
# end::exercise7[]
'''


# tag::answer7[]
def bip91(self):
    return self.version >> 4 & 1 == 1
# end::answer7[]


'''
# tag::exercise8[]
==== Ćwiczenie 8

Napisz metodę `bip141` dla klasy `Block`.
# end::exercise8[]
'''


# tag::answer8[]
def bip141(self):
    return self.version >> 1 & 1 == 1
# end::answer8[]


'''
# tag::exercise9[]
==== Ćwiczenie 9

Dopisz funkcję `bits_to_target` do pliku _helper.py_.
# end::exercise9[]
'''


# tag::answer9[]
def bits_to_target(bits):
    exponent = bits[-1]
    coefficient = little_endian_to_int(bits[:-1])
    return coefficient * 256**(exponent - 3)
# end::answer9[]


def target(self):
    return bits_to_target(self.bits)


'''
# tag::exercise10[]
==== Ćwiczenie 10

Napisz metodę `difficulty` dla klasy `Block`.
# end::exercise10[]
'''


# tag::answer10[]
def difficulty(self):
    lowest = 0xffff * 256**(0x1d - 3)
    return lowest / self.target()
# end::answer10[]


'''
# tag::exercise11[]
==== Ćwiczenie 11

Napisz metodę `check_pow` dla klasy `Block`.

# end::exercise11[]
'''


# tag::answer11[]
def check_pow(self):
    sha = hash256(self.serialize())
    proof = little_endian_to_int(sha)
    return proof < self.target()
# end::answer11[]


'''
# tag::exercise13[]
==== Ćwiczenie 13

Dopisz funkcję `calculate_new_bits` do pliku _helper.py_.
# end::exercise13[]
'''


# tag::answer13[]
def calculate_new_bits(previous_bits, time_differential):
    if time_differential > TWO_WEEKS * 4:
        time_differential = TWO_WEEKS * 4
    if time_differential < TWO_WEEKS // 4:
        time_differential = TWO_WEEKS // 4
    new_target = bits_to_target(previous_bits) * time_differential // TWO_WEEKS
    return target_to_bits(new_target)
# end::answer13[]


class ChapterTest(TestCase):

    def test_apply(self):
        Tx.is_coinbase = is_coinbase
        Tx.coinbase_height = coinbase_height
        Block.parse = parse
        Block.serialize = serialize
        Block.hash = hash
        Block.bip9 = bip9
        Block.bip91 = bip91
        Block.bip141 = bip141
        Block.difficulty = difficulty
        Block.check_pow = check_pow
        Block.target = target
        helper.calculate_new_bits = calculate_new_bits
        helper.bits_to_target = bits_to_target
