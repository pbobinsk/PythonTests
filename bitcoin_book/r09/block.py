from io import BytesIO
from unittest import TestCase

from helper import (
    bits_to_target,
    hash256,
    int_to_little_endian,
    little_endian_to_int,
)


# tag::source1[]
class Block:

    def __init__(self, version, prev_block, merkle_root, timestamp, bits, nonce):
        self.version = version
        self.prev_block = prev_block
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.bits = bits
        self.nonce = nonce
    # end::source1[]

    @classmethod
    def parse(cls, s):
        '''Przetwarza blok w strumieniu bajtów. Zwraca obiekt typu Block'''
        # s.read(n) czyta n bajtów ze strumienia
        # wersja - 4 bajty, little endian, interpretowane jako int
        # prev_block - 32 bajty, little endian (użyj [:: - 1], aby odwrócić ciąg)
        # merkle_root - 32 bajty, little endian (użyj [:: - 1] aby odwrócić ciąg)
        # znacznik czasu - 4 bajty, little endian, interpretowane jako int
        # bity - 4 bajty
        # nonce - 4 bajty
        # zainicjuj klasę
        raise NotImplementedError

    def serialize(self):
        '''Zwraca 80-bajtowy nagłówek bloku'''
        # wersja  - 4 bajty, little endian
        # prev_block - 32 bajty, little endian
        # markle_root - 32 bajty, little endian
        # znacznik czasu - 4 bajty, little endian
        # bity - 4 bajty
        # nonce - 4 bajty
        raise NotImplementedError

    def hash(self):
        '''Zwraca zinterpretowany skrót hash256 bloku, little endian'''
        # serializuj
        # hash256
        # odwróć
        raise NotImplementedError

    def bip9(self):
        '''Określa, czy ten blok zgłasza gotowość obsługi BIP9'''
        # BIP9 sygnalizuje, jeśli najwyższe 3 bity, to 001
        # pamiętaj, że wersja zajmuje 32 bajty, więc trzeba przesunąć o 29 miejsc w prawo (>> 29) 
        # i sprawdzić, czy to 001
        raise NotImplementedError

    def bip91(self):
        '''Określa, czy ten blok zgłasza gotowość obsługi BIP91'''
        # Gotowość BIP91 sygnalizuje ustawiony 5. bit od prawej
        # przesuń 4 bity w prawo i sprawdź, czy ostatni bit ma wartość 1
        raise NotImplementedError

    def bip141(self):
        '''Określa, czy ten blok zgłasza gotowość obsługi BIP141'''
        # Gotowość BIP91 sygnalizuje ustawiony 2. bit od prawej
        # przesuń o 1 bit w prawo i sprawdź, czy ostatni bit ma wartość 1
        raise NotImplementedError

    def target(self):
        '''Zwraca cel dla dowodu pracy określony na podstawie bitów'''
        return bits_to_target(self.bits)

    def difficulty(self):
        '''Zwraca trudność bloku określoną na podstawie bitów'''
        # pamiętaj, że trudność, to: (cel najniższej trudności) / (cel self)
        # bity najniższej trudności to 0xffff001d
        raise NotImplementedError

    def check_pow(self):
        '''Sprawdza, czy ten blok spełnia dowód pracy'''
        # weź skrót hash256 serializacji tego bloku
        # zinterpretuj ten skrót jako liczbę little endian
        # zwróć prawdę, jeśli ta liczba całkowita jest mniejsza niż cel
        raise NotImplementedError


class BlockTest(TestCase):

    def test_parse(self):
        block_raw = bytes.fromhex('020000208ec39428b17323fa0ddec8e887b4a7c53b8c0a0a220cfd0000000000000000005b0750fce0a889502d40508d39576821155e9c9e3f5c3157f961db38fd8b25be1e77a759e93c0118a4ffd71d')
        stream = BytesIO(block_raw)
        block = Block.parse(stream)
        self.assertEqual(block.version, 0x20000002)
        want = bytes.fromhex('000000000000000000fd0c220a0a8c3bc5a7b487e8c8de0dfa2373b12894c38e')
        self.assertEqual(block.prev_block, want)
        want = bytes.fromhex('be258bfd38db61f957315c3f9e9c5e15216857398d50402d5089a8e0fc50075b')
        self.assertEqual(block.merkle_root, want)
        self.assertEqual(block.timestamp, 0x59a7771e)
        self.assertEqual(block.bits, bytes.fromhex('e93c0118'))
        self.assertEqual(block.nonce, bytes.fromhex('a4ffd71d'))

    def test_serialize(self):
        block_raw = bytes.fromhex('020000208ec39428b17323fa0ddec8e887b4a7c53b8c0a0a220cfd0000000000000000005b0750fce0a889502d40508d39576821155e9c9e3f5c3157f961db38fd8b25be1e77a759e93c0118a4ffd71d')
        stream = BytesIO(block_raw)
        block = Block.parse(stream)
        self.assertEqual(block.serialize(), block_raw)

    def test_hash(self):
        block_raw = bytes.fromhex('020000208ec39428b17323fa0ddec8e887b4a7c53b8c0a0a220cfd0000000000000000005b0750fce0a889502d40508d39576821155e9c9e3f5c3157f961db38fd8b25be1e77a759e93c0118a4ffd71d')
        stream = BytesIO(block_raw)
        block = Block.parse(stream)
        self.assertEqual(block.hash(), bytes.fromhex('0000000000000000007e9e4c586439b0cdbe13b1370bdd9435d76a644d047523'))

    def test_bip9(self):
        block_raw = bytes.fromhex('020000208ec39428b17323fa0ddec8e887b4a7c53b8c0a0a220cfd0000000000000000005b0750fce0a889502d40508d39576821155e9c9e3f5c3157f961db38fd8b25be1e77a759e93c0118a4ffd71d')
        stream = BytesIO(block_raw)
        block = Block.parse(stream)
        self.assertTrue(block.bip9())
        block_raw = bytes.fromhex('0400000039fa821848781f027a2e6dfabbf6bda920d9ae61b63400030000000000000000ecae536a304042e3154be0e3e9a8220e5568c3433a9ab49ac4cbb74f8df8e8b0cc2acf569fb9061806652c27')
        stream = BytesIO(block_raw)
        block = Block.parse(stream)
        self.assertFalse(block.bip9())

    def test_bip91(self):
        block_raw = bytes.fromhex('1200002028856ec5bca29cf76980d368b0a163a0bb81fc192951270100000000000000003288f32a2831833c31a25401c52093eb545d28157e200a64b21b3ae8f21c507401877b5935470118144dbfd1')
        stream = BytesIO(block_raw)
        block = Block.parse(stream)
        self.assertTrue(block.bip91())
        block_raw = bytes.fromhex('020000208ec39428b17323fa0ddec8e887b4a7c53b8c0a0a220cfd0000000000000000005b0750fce0a889502d40508d39576821155e9c9e3f5c3157f961db38fd8b25be1e77a759e93c0118a4ffd71d')
        stream = BytesIO(block_raw)
        block = Block.parse(stream)
        self.assertFalse(block.bip91())

    def test_bip141(self):
        block_raw = bytes.fromhex('020000208ec39428b17323fa0ddec8e887b4a7c53b8c0a0a220cfd0000000000000000005b0750fce0a889502d40508d39576821155e9c9e3f5c3157f961db38fd8b25be1e77a759e93c0118a4ffd71d')
        stream = BytesIO(block_raw)
        block = Block.parse(stream)
        self.assertTrue(block.bip141())
        block_raw = bytes.fromhex('0000002066f09203c1cf5ef1531f24ed21b1915ae9abeb691f0d2e0100000000000000003de0976428ce56125351bae62c5b8b8c79d8297c702ea05d60feabb4ed188b59c36fa759e93c0118b74b2618')
        stream = BytesIO(block_raw)
        block = Block.parse(stream)
        self.assertFalse(block.bip141())

    def test_target(self):
        block_raw = bytes.fromhex('020000208ec39428b17323fa0ddec8e887b4a7c53b8c0a0a220cfd0000000000000000005b0750fce0a889502d40508d39576821155e9c9e3f5c3157f961db38fd8b25be1e77a759e93c0118a4ffd71d')
        stream = BytesIO(block_raw)
        block = Block.parse(stream)
        self.assertEqual(block.target(), 0x13ce9000000000000000000000000000000000000000000)
        self.assertEqual(int(block.difficulty()), 888171856257)

    def test_difficulty(self):
        block_raw = bytes.fromhex('020000208ec39428b17323fa0ddec8e887b4a7c53b8c0a0a220cfd0000000000000000005b0750fce0a889502d40508d39576821155e9c9e3f5c3157f961db38fd8b25be1e77a759e93c0118a4ffd71d')
        stream = BytesIO(block_raw)
        block = Block.parse(stream)
        self.assertEqual(int(block.difficulty()), 888171856257)

    def test_check_pow(self):
        block_raw = bytes.fromhex('04000000fbedbbf0cfdaf278c094f187f2eb987c86a199da22bbb20400000000000000007b7697b29129648fa08b4bcd13c9d5e60abb973a1efac9c8d573c71c807c56c3d6213557faa80518c3737ec1')
        stream = BytesIO(block_raw)
        block = Block.parse(stream)
        self.assertTrue(block.check_pow())
        block_raw = bytes.fromhex('04000000fbedbbf0cfdaf278c094f187f2eb987c86a199da22bbb20400000000000000007b7697b29129648fa08b4bcd13c9d5e60abb973a1efac9c8d573c71c807c56c3d6213557faa80518c3737ec0')
        stream = BytesIO(block_raw)
        block = Block.parse(stream)
        self.assertFalse(block.check_pow())
