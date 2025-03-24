from unittest import TestCase

from helper import (
    bit_field_to_bytes,
    encode_varint,
    int_to_little_endian,
    murmur3,
)
from network import GenericMessage


BIP37_CONSTANT = 0xfba4c795


class BloomFilter:

    def __init__(self, size, function_count, tweak):
        self.size = size
        self.bit_field = [0] * (size * 8)
        self.function_count = function_count
        self.tweak = tweak

    def add(self, item):
        '''Dodaj element do filtra'''
        # iteruj self.function_count ileś razy
        for i in range(self.function_count):
            # ziarno według spec. BIP0037 to i*BIP37_CONSTANT + self.tweak
            seed = i * BIP37_CONSTANT + self.tweak
            # oblicz skrót murmur3, podając to ziarno
            h = murmur3(item, seed=seed)
            # ustaw bit jako skrót modulo rozmiar pola bitowego (self.size * 8)
            bit = h % (self.size * 8)
            # ustaw bit pola bitów na 1
            self.bit_field[bit] = 1

    def filter_bytes(self):
        return bit_field_to_bytes(self.bit_field)

    def filterload(self, flag=1):
        '''Zwróć komunikat filterload'''
        # rozpocznij od rozmiaru filtra w bajtach
        payload = encode_varint(self.size)
        # następnie dodaj pole bitowe za pomocą self.filter_bytes()
        payload += self.filter_bytes()
        # liczba funkcji: 4 bajty, little endian
        payload += int_to_little_endian(self.function_count, 4)
        # tweak: 4 bajty, little endian
        payload += int_to_little_endian(self.tweak, 4)
        # flaga: 1 bajt, little endian
        payload += int_to_little_endian(flag, 1)
        # zwróć komunikat GenericMessage, którego polecenie 
        # to b'filterload' i treść, czyli to, co obliczyliśmy
        return GenericMessage(b'filterload', payload)


class BloomFilterTest(TestCase):

    def test_add(self):
        bf = BloomFilter(10, 5, 99)
        item = b'Hello World'
        bf.add(item)
        expected = '0000000a080000000140'
        self.assertEqual(bf.filter_bytes().hex(), expected)
        item = b'Goodbye!'
        bf.add(item)
        expected = '4000600a080000010940'
        self.assertEqual(bf.filter_bytes().hex(), expected)

    def test_filterload(self):
        bf = BloomFilter(10, 5, 99)
        item = b'Hello World'
        bf.add(item)
        item = b'Goodbye!'
        bf.add(item)
        expected = '0a4000600a080000010940050000006300000001'
        self.assertEqual(bf.filterload().serialize().hex(), expected)
