from unittest import TestCase, TestSuite, TextTestRunner

import hashlib


SIGHASH_ALL = 1
SIGHASH_NONE = 2
SIGHASH_SINGLE = 3
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
TWO_WEEKS = 60 * 60 * 24 * 14
MAX_TARGET = 0xffff * 256**(0x1d - 3)


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
    if testnet:
        prefix = b'\x6f'
    else:
        prefix = b'\x00'
    return encode_base58_checksum(prefix + h160)


def h160_to_p2sh_address(h160, testnet=False):
    '''Dla skrótu hash160 ciągu bajtów zwraca łańcuch adresu p2sh '''
    # p2sh ma prefiks b'\x05’ dla mainnetu, b'\xc4' dla testnetu
    if testnet:
        prefix = b'\xc4'
    else:
        prefix = b'\x05'
    return encode_base58_checksum(prefix + h160)


def bits_to_target(bits):
    '''Przekształca bity na cel (dużą 256-bitową liczbę całkowitą)'''
    # ostatni bajt jest wykładnikiem
    exponent = bits[-1]
    # pierwsze trzy bajty to współczynnik w kodowaniu little endian
    coefficient = little_endian_to_int(bits[:-1])
    # wzór to:
    # współczynnik * 256**(wykładnik-3)
    return coefficient * 256**(exponent - 3)


def target_to_bits(target):
    '''Zamienia wartość celu z liczby całkowitej na reprezentację bitową'''
    raw_bytes = target.to_bytes(32, 'big')
    # pozbądź się wiodących zer
    raw_bytes = raw_bytes.lstrip(b'\x00')
    if raw_bytes[0] > 0x7f:
        # jeśli pierwszy bit ma wartość 1, musimy zacząć od 00
        exponent = len(raw_bytes) + 1
        coefficient = b'\x00' + raw_bytes[:2]
    else:
        # w przeciwnym razie możemy pokazać pierwsze 3 bajty
        # wykładnik, to liczba znaczących cyfr dla zapisu w systemie po podstawie 256
        exponent = len(raw_bytes)
        # współczynnik, to pierwsze trzy cyfry liczby w systemie o podstawie 256
        coefficient = raw_bytes[:3]
    # zaokrągliliśmy tą liczbę po pierwszych 3 cyfrach w systemie base-256
    new_bits = coefficient[::-1] + bytes([exponent])
    return new_bits


def calculate_new_bits(previous_bits, time_differential):
    '''Oblicza nowe bity dla różnicy czasu 2016 bloków i poprzednich bitów'''
    # jeśli różnica czasu jest większa, niż 8 tygodni, przypisz jej 8 tygodni
    if time_differential > TWO_WEEKS * 4:
        time_differential = TWO_WEEKS * 4
    # jeśli różnica czasu jest mniejsza, niż pół tygodnia, przypisz jej pół tygodnia
    if time_differential < TWO_WEEKS // 4:
        time_differential = TWO_WEEKS // 4 
    # nowy cel to poprzedni cel * różnica czasu / dwa tygodnie
    new_target = bits_to_target(previous_bits) * time_differential // TWO_WEEKS
    # jeśli nowy cel jest większy niż MAX_TARGET, przypisz mu wartość MAX_TARGET
    if new_target > MAX_TARGET:
        new_target = MAX_TARGET
    # skonwertuj nowy cel na bity
    return target_to_bits(new_target)


def merkle_parent(hash1, hash2):
    '''Dla skrótów w postaci binarnej oblicza hash256'''
    # zwróć hash256 dla hash1 + hash2
    raise NotImplementedError


def merkle_parent_level(hashes):
    '''Dla listy skrótów binarnych zwraca listę o połowie długości'''
    # jeśli lista zawiera dokładnie 1 element, zgłoś błąd
    # jeśli lista zawiera nieparzystą liczbę elementów, powiel ostatni
    # i umieść go na końcu, aby liczba elementów była parzysta
    # zainicjuj następny poziom
    # wykonaj w pętli dla każdej pary (użyj: for i in range (0, len (hashes), 2))
        # pobierz el. nadrzędny drzewa skrótów o indeksie i oraz i+1
        # dołącz element nadrzędny do poziomu nadrzędnego
    # zwróć poziom nadrzędny
    raise NotImplementedError


def merkle_root(hashes):
    '''Dla listy skrótów binarnych zwróć korzeń drzewa skrótów'''
    # bieżący poziom zaczyna się od skrótów
    # wykonaj w pętli, aż pozostanie dokładnie 1 element
        # bieżący poziom staje się poziomem nadrzędnym drzewa skrótów
    # zwróć 1. pozycję bieżącego poziomu
    raise NotImplementedError


def bit_field_to_bytes(bit_field):
    if len(bit_field) % 8 != 0:
        raise RuntimeError('bit_field nie ma długości podzielnej przez 8')
    result = bytearray(len(bit_field) // 8)
    for i, bit in enumerate(bit_field):
        byte_index, bit_index = divmod(i, 8)
        if bit:
            result[byte_index] |= 1 << bit_index
    return bytes(result)


# tag::source1[]
def bytes_to_bit_field(some_bytes):
    flag_bits = []
    for byte in some_bytes:
        for _ in range(8):
            flag_bits.append(byte & 1)
            byte >>= 1
    return flag_bits
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

    def test_calculate_new_bits(self):
        prev_bits = bytes.fromhex('54d80118')
        time_differential = 302400
        want = bytes.fromhex('00157617')
        self.assertEqual(calculate_new_bits(prev_bits, time_differential), want)

    def test_merkle_parent(self):
        tx_hash0 = bytes.fromhex('c117ea8ec828342f4dfb0ad6bd140e03a50720ece40169ee38bdc15d9eb64cf5')
        tx_hash1 = bytes.fromhex('c131474164b412e3406696da1ee20ab0fc9bf41c8f05fa8ceea7a08d672d7cc5')
        want = bytes.fromhex('8b30c5ba100f6f2e5ad1e2a742e5020491240f8eb514fe97c713c31718ad7ecd')
        self.assertEqual(merkle_parent(tx_hash0, tx_hash1), want)

    def test_merkle_parent_level(self):
        hex_hashes = [
            'c117ea8ec828342f4dfb0ad6bd140e03a50720ece40169ee38bdc15d9eb64cf5',
            'c131474164b412e3406696da1ee20ab0fc9bf41c8f05fa8ceea7a08d672d7cc5',
            'f391da6ecfeed1814efae39e7fcb3838ae0b02c02ae7d0a5848a66947c0727b0',
            '3d238a92a94532b946c90e19c49351c763696cff3db400485b813aecb8a13181',
            '10092f2633be5f3ce349bf9ddbde36caa3dd10dfa0ec8106bce23acbff637dae',
            '7d37b3d54fa6a64869084bfd2e831309118b9e833610e6228adacdbd1b4ba161',
            '8118a77e542892fe15ae3fc771a4abfd2f5d5d5997544c3487ac36b5c85170fc',
            'dff6879848c2c9b62fe652720b8df5272093acfaa45a43cdb3696fe2466a3877',
            'b825c0745f46ac58f7d3759e6dc535a1fec7820377f24d4c2c6ad2cc55c0cb59',
            '95513952a04bd8992721e9b7e2937f1c04ba31e0469fbe615a78197f68f52b7c',
            '2e6d722e5e4dbdf2447ddecc9f7dabb8e299bae921c99ad5b0184cd9eb8e5908',
        ]
        tx_hashes = [bytes.fromhex(x) for x in hex_hashes]
        want_hex_hashes = [
            '8b30c5ba100f6f2e5ad1e2a742e5020491240f8eb514fe97c713c31718ad7ecd',
            '7f4e6f9e224e20fda0ae4c44114237f97cd35aca38d83081c9bfd41feb907800',
            'ade48f2bbb57318cc79f3a8678febaa827599c509dce5940602e54c7733332e7',
            '68b3e2ab8182dfd646f13fdf01c335cf32476482d963f5cd94e934e6b3401069',
            '43e7274e77fbe8e5a42a8fb58f7decdb04d521f319f332d88e6b06f8e6c09e27',
            '1796cd3ca4fef00236e07b723d3ed88e1ac433acaaa21da64c4b33c946cf3d10',
        ]
        want_tx_hashes = [bytes.fromhex(x) for x in want_hex_hashes]
        self.assertEqual(merkle_parent_level(tx_hashes), want_tx_hashes)

    def test_merkle_root(self):
        hex_hashes = [
            'c117ea8ec828342f4dfb0ad6bd140e03a50720ece40169ee38bdc15d9eb64cf5',
            'c131474164b412e3406696da1ee20ab0fc9bf41c8f05fa8ceea7a08d672d7cc5',
            'f391da6ecfeed1814efae39e7fcb3838ae0b02c02ae7d0a5848a66947c0727b0',
            '3d238a92a94532b946c90e19c49351c763696cff3db400485b813aecb8a13181',
            '10092f2633be5f3ce349bf9ddbde36caa3dd10dfa0ec8106bce23acbff637dae',
            '7d37b3d54fa6a64869084bfd2e831309118b9e833610e6228adacdbd1b4ba161',
            '8118a77e542892fe15ae3fc771a4abfd2f5d5d5997544c3487ac36b5c85170fc',
            'dff6879848c2c9b62fe652720b8df5272093acfaa45a43cdb3696fe2466a3877',
            'b825c0745f46ac58f7d3759e6dc535a1fec7820377f24d4c2c6ad2cc55c0cb59',
            '95513952a04bd8992721e9b7e2937f1c04ba31e0469fbe615a78197f68f52b7c',
            '2e6d722e5e4dbdf2447ddecc9f7dabb8e299bae921c99ad5b0184cd9eb8e5908',
            'b13a750047bc0bdceb2473e5fe488c2596d7a7124b4e716fdd29b046ef99bbf0',
        ]
        tx_hashes = [bytes.fromhex(x) for x in hex_hashes]
        want_hex_hash = 'acbcab8bcc1af95d8d563b77d24c3d19b18f1486383d75a5085c4e86c86beed6'
        want_hash = bytes.fromhex(want_hex_hash)
        self.assertEqual(merkle_root(tx_hashes), want_hash)
