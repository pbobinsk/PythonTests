from unittest import TestSuite, TextTestRunner, TestLoader

import hashlib


try:
    import bech32
    BECH32_IMPLEMENTED = True
except ImportError:
    BECH32_IMPLEMENTED = False
    print("UWAGA: Biblioteka 'bech32' nie jest zainstalowana.")
    print("Aby wygenerować adresy SegWit (Bech32), zainstaluj ją: pip install bech32")

def run(test):
    suite = TestSuite()
    suite.addTest(test)
    TextTestRunner().run(suite)

def run_all(test_case_class):
    suite = TestLoader().loadTestsFromTestCase(test_case_class)
    TextTestRunner().run(suite)

def hash256(s):
    '''dwukrotne obliczenia skrótu sha256'''
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

SIGHASH_ALL = 1
SIGHASH_NONE = 2
SIGHASH_SINGLE = 3

BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def hash160(s):
    '''sha256, a następnie ripemd160'''
    return hashlib.new('ripemd160', hashlib.sha256(s).digest()).digest()  # <1>

def encode_base58(s):
    count = 0
    for c in s:  # <1>
        if c == 0:
            count += 1
        else:
            break
    num = int.from_bytes(s, 'big')
    prefix = '1' * count
    result = ''
    while num > 0:  # <2>
        num, mod = divmod(num, 58)
        result = BASE58_ALPHABET[mod] + result
    return prefix + result  # <3>
# end::source2[]


# tag::source3[]
def encode_base58_checksum(b):
    return encode_base58(b + hash256(b)[:4])
# end::source3[]


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
    # wykorzystaj int.from_bytes()
    return int.from_bytes(b, 'little')


def int_to_little_endian(n, length):
    '''int_to_little_endian dla liczby całkowitej zwraca sekwencję bajtową
    w porządku little endian o długości'''
    # wykorzystaj n.to_bytes()
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
    if testnet:
        prefix = b'\x6f'
    else:
        prefix = b'\x00'
    return encode_base58_checksum(prefix + h160)

def h160_to_p2sh_address(h160, testnet=False):
    '''Dla skrótu hash160 ciągu bajtów zwraca łańcuch adresu p2sh '''
    if testnet:
        prefix = b'\xc4'
    else:
        prefix = b'\x05'
    return encode_base58_checksum(prefix + h160)

