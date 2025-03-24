from unittest import TestCase, TestSuite, TextTestRunner

import hashlib


BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def run(test):
    suite = TestSuite()
    suite.addTest(test)
    TextTestRunner().run(suite)


def hash160(s):
    '''sha256, a następnie ripemd160'''
    return hashlib.new('ripemd160', hashlib.sha256(s).digest()).digest()


def hash256(s):
    '''dwukrotne obliczenia skrótu sha256'''
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()


def encode_base58(s):
    # określ, od ilu bajtów o wartości 0 (b '\x00') zaczyna się s
    count = 0
    for c in s:
        if c == 0:
            count += 1
        else:
            break
    # konwersja na liczbę całkowitą w porządku big endian
    num = int.from_bytes(s, 'big')
    prefix = '1' * count
    result = ''
    while num > 0:
        num, mod = divmod(num, 58)
        result = BASE58_ALPHABET[mod] + result
    return prefix + result


def encode_base58_checksum(s):
    return encode_base58(s + hash256(s)[:4])


def decode_base58(s):
    num = 0
    for c in s:
        num *= 58
        num += BASE58_ALPHABET.index(c)
    combined = num.to_bytes(25, byteorder='big')
    checksum = combined[-4:]
    if hash256(combined[:-4])[:4] != checksum:
        raise ValueError('zły adres: {} {}'.format(checksum, hash256(combined[:-4])[:4]))
    return combined[1:-4]


def little_endian_to_int(b):
    '''sekwencja bajtowa dla little_endian_to_int powinna być liczbą little endian.
    Zwraca liczbę całkowitą'''
    return int.from_bytes(b, 'little')


def int_to_little_endian(n, length):
    '''int_to_little_endian dla liczby całkowitej zwraca sekwencję bajtową
    w porządku little endian o długości'''
    return n.to_bytes(length, 'little')


# tag::source1[]
def read_varint(s):
    '''read_varint odczytuje wartość typu varint ze strumienia'''
    i = s.read(1)[0]
    if i == 0xfd:
        # 0xfd oznacza, że 2 kolejne bajty określają wartość
        return little_endian_to_int(s.read(2))
    elif i == 0xfe:
        # 0xfe oznacza, że 4 kolejne bajty określają wartość
        return little_endian_to_int(s.read(4))
    elif i == 0xff:
        # 0xff oznacza, że 8 kolejnych bajtów określa wartość
        return little_endian_to_int(s.read(8))
    else:
        # Każda inna wartość to po prostu liczba całkowita
        return i


def encode_varint(i):
    '''Koduje wartość integer, w formacie varint'''
    if i < 0xfd:
        return bytes([i])
    elif i < 0x10000:
        return b'\xfd' + int_to_little_endian(i, 2)
    elif i < 0x100000000:
        return b'\xfe' + int_to_little_endian(i, 4)
    elif i < 0x10000000000000000:
        return b'\xff' + int_to_little_endian(i, 8)
    else:
        raise ValueError('za duża wartość typu int: {}'.format(i))
# end::source1[]


class HelperTest(TestCase):

    def test_little_endian_to_int(self):
        h = bytes.fromhex('99c3980000000000')
        want = 10011545
        self.assertEqual(little_endian_to_int(h), want)
        h = bytes.fromhex('a135ef0100000000')
        want = 32454049
        self.assertEqual(little_endian_to_int(h), want)

    def test_int_to_little_endian(self):
        n = 1
        want = b'\x01\x00\x00\x00'
        self.assertEqual(int_to_little_endian(n, 4), want)
        n = 10011545
        want = b'\x99\xc3\x98\x00\x00\x00\x00\x00'
        self.assertEqual(int_to_little_endian(n, 8), want)
