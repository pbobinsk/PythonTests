'''
# tag::answer5[]
>>> import math
>>> total = 27
>>> max_depth = math.ceil(math.log(total, 2))
>>> merkle_tree = []
>>> for depth in range(max_depth + 1):
...     num_items = math.ceil(total / 2**(max_depth - depth))
...     level_hashes = [None] * num_items
...     merkle_tree.append(level_hashes)
>>> for level in merkle_tree:
...     print(level)
[None]
[None, None]
[None, None, None, None]
[None, None, None, None, None, None, None]
[None, None, None, None, None, None, None, None, None, None, None, None, None,\
 None]
[None, None, None, None, None, None, None, None, None, None, None, None, None,\
 None, None, None, None, None, None, None, None, None, None, None, None, None,\
 None]

# end::answer5[]
'''


from unittest import TestCase

import helper
import merkleblock

from block import Block
from helper import (
    bytes_to_bit_field,
    hash256,
    little_endian_to_int,
    read_varint,
)
from merkleblock import (
    MerkleBlock,
    MerkleTree,
)


'''
# tag::exercise1[]
==== Ćwiczenie 1

Napisz funkcję `merkle_parent`.
# end::exercise1[]
'''


# tag::answer1[]
def merkle_parent(hash1, hash2):
    '''Dla skrótów w postaci binarnej oblicza hash256'''
    return hash256(hash1 + hash2)
# end::answer1[]


'''
# tag::exercise2[]
==== Ćwiczenie 2

Napisz funkcję `merkle_parent_level`.
# end::exercise2[]
'''


# tag::answer2[]
def merkle_parent_level(hashes):
    '''Dla listy skrótów binarnych zwraca listę o połowie długości'''
    if len(hashes) == 1:
        raise RuntimeError('Błąd! Poziom nadrzędny ma tylko 1 element')
    if len(hashes) % 2 == 1:
        hashes.append(hashes[-1])
    parent_level = []
    for i in range(0, len(hashes), 2):
        parent = merkle_parent(hashes[i], hashes[i + 1])
        parent_level.append(parent)
    return parent_level
# end::answer2[]


'''
# tag::exercise3[]
==== Ćwiczenie 3

Napisz funkcję `merkle_root`.
# end::exercise3[]
'''


# tag::answer3[]
def merkle_root(hashes):
   '''Dla listy skrótów binarnych zwraca korzeń drzewa skrótów'''
    current_level = hashes
    while len(current_level) > 1:
        current_level = merkle_parent_level(current_level)
    return current_level[0]
# end::answer3[]


'''
# tag::exercise4[]
==== Ćwiczenie 4

Napisz metodę `validate_merkle_root` dla klasy `Block`.
# end::exercise4[]
'''


# tag::answer4[]
def validate_merkle_root(self):
    hashes = [h[::-1] for h in self.tx_hashes]
    root = merkle_root(hashes)
    return root[::-1] == self.merkle_root
# end::answer4[]


'''
# tag::exercise5[]
==== Ćwiczenie 5

Utwórz puste drzewo skrótów z 27 elementami i wydrukuj każdy poziom.
# end::exercise5[]
'''
'''
# tag::exercise6[]
==== Ćwiczenie 6

Napisz metodę `parse` dla klasy `MerkleBlock`.
# end::exercise6[]
'''


# tag::answer6[]
@classmethod
def parse(cls, s):
    version = little_endian_to_int(s.read(4))
    prev_block = s.read(32)[::-1]
    merkle_root = s.read(32)[::-1]
    timestamp = little_endian_to_int(s.read(4))
    bits = s.read(4)
    nonce = s.read(4)
    total = little_endian_to_int(s.read(4))
    num_hashes = read_varint(s)
    hashes = []
    for _ in range(num_hashes):
        hashes.append(s.read(32)[::-1])
    flags_length = read_varint(s)
    flags = s.read(flags_length)
    return cls(version, prev_block, merkle_root, timestamp, bits,
               nonce, total, hashes, flags)
# end::answer6[]


'''
# tag::exercise7[]
==== Ćwiczenie 7

Napisz metodę `is_valid` dla klasy `MerkleBlock`.
# end::exercise7[]
'''


# tag::answer7[]
def is_valid(self):
    flag_bits = bytes_to_bit_field(self.flags)
    hashes = [h[::-1] for h in self.hashes]
    merkle_tree = MerkleTree(self.total)
    merkle_tree.populate_tree(flag_bits, hashes)
    return merkle_tree.root()[::-1] == self.merkle_root
# end::answer7[]


class ChapterTest(TestCase):

    def test_apply(self):
        helper.merkle_parent = merkle_parent
        merkleblock.merkle_parent = merkle_parent
        helper.merkle_parent_level = merkle_parent_level
        helper.merkle_root = merkle_root
        Block.validate_merkle_root = validate_merkle_root
        MerkleBlock.parse = parse
        MerkleBlock.is_valid = is_valid
