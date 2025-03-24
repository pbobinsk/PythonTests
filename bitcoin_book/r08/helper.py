from unittest import TestCase, TestSuite, TextTestRunner

import hashlib


SIGHASH_ALL = 1
SIGHASH_NONE = 2
SIGHASH_SINGLE = 3
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


def h160_to_p2pkh_address(h160, testnet=False):
    '''Dla skrótu hash160 ciągu bajtów zwraca łańcuch adresu p2pkh'''
    # p2pkh ma prefiks b'\x00’ dla mainnetu, b'\x6f' dla testnetu
    # aby otrzymać adres, użyj encode_base58_checksum
    raise NotImplementedError


def h160_to_p2sh_address(h160, testnet=False):
    '''Dla skrótu hash160 ciągu bajtów zwraca łańcuch adresu p2sh '''
    # p2sh ma prefiks b'\x05’ dla mainnetu, b'\xc4' dla testnetu
    # aby otrzymać adres, użyj encode_base58_checksum
    raise NotImplementedError


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

    def test_base58(self):
        addr = 'mnrVtF8DWjMu839VW3rBfgYaAfKk8983Xf'
        h160 = decode_base58(addr).hex()
        want = '507b27411ccf7f16f10297de6cef3f291623eddf'
        self.assertEqual(h160, want)
        got = encode_base58_checksum(b'\x6f' + bytes.fromhex(h160))
        self.assertEqual(got, addr)

    def test_p2pkh_address(self):
        h160 = bytes.fromhex('74d691da1574e6b3c192ecfb52cc8984ee7b6c56')
        want = '1BenRpVUFK65JFWcQSuHnJKzc4M8ZP8Eqa'
        self.assertEqual(h160_to_p2pkh_address(h160, testnet=False), want)
        want = 'mrAjisaT4LXL5MzE81sfcDYKU3wqWSvf9q'
        self.assertEqual(h160_to_p2pkh_address(h160, testnet=True), want)

    def test_p2sh_address(self):
        h160 = bytes.fromhex('74d691da1574e6b3c192ecfb52cc8984ee7b6c56')
        want = '3CLoMMyuoDQTPRD3XYZtCvgvkadrAdvdXh'
        self.assertEqual(h160_to_p2sh_address(h160, testnet=False), want)
        want = '2N3u1R6uwQfuobCqbCgBkpsgBxvr1tZpe7B'
        self.assertEqual(h160_to_p2sh_address(h160, testnet=True), want)
