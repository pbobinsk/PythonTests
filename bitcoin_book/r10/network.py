import socket
import time

from io import BytesIO
from random import randint
from unittest import TestCase

from block import Block
from helper import (
    hash256,
    encode_varint,
    int_to_little_endian,
    little_endian_to_int,
    read_varint,
)


# tag::source1[]
NETWORK_MAGIC = b'\xf9\xbe\xb4\xd9'
TESTNET_NETWORK_MAGIC = b'\x0b\x11\x09\x07'


class NetworkEnvelope:

    def __init__(self, command, payload, testnet=False):
        self.command = command
        self.payload = payload
        if testnet:
            self.magic = TESTNET_NETWORK_MAGIC
        else:
            self.magic = NETWORK_MAGIC

    def __repr__(self):
        return '{}: {}'.format(
            self.command.decode('ascii'),
            self.payload.hex(),
        )
    # end::source1[]

    @classmethod
    def parse(cls, s, testnet=False):
        '''Dla strumienia tworzy NetworkEnvelope'''
        # sprawdź wartość network magic
        magic = s.read(4)
        if magic == b'':
            raise RuntimeError('Połączenie zresetowane!')
        if testnet:
            expected_magic = TESTNET_NETWORK_MAGIC
        else:
            expected_magic = NETWORK_MAGIC
        if magic != expected_magic:
            raise RuntimeError('wartość magic niepoprawna {} vs {}'.format(magic.hex(), expected_magic.hex()))
        # polecenie 12 bajtów
        # usuń końcowe zera
        # długość treści 4 bajty, little endian
        # suma kontrolna 4 bajty, pierwsze cztery bajty skrótu hash256 treści
        # treść ma długość payload_length
        # zweryfikuj sumę kontrolną
        # zwróć instancję tej klasy
        raise NotImplementedError

    def serialize(self):
        '''Zwraca bajtową serializację całego komunikatu sieciowego'''
        # dodaj wartość network magic
        # polecenie 12 bajtów
        # uzupełnij zerami
        # długość treści 4 bajty, little endian
        # suma kontrolna 4 bajty, pierwsze cztery bajty skrótu hash256 treści
        # treść
        raise NotImplementedError

    def stream(self):
        '''Zwraca strumień do przetwarzania treści'''
        return BytesIO(self.payload)


class NetworkEnvelopeTest(TestCase):

    def test_parse(self):
        msg = bytes.fromhex('f9beb4d976657261636b000000000000000000005df6e0e2')
        stream = BytesIO(msg)
        envelope = NetworkEnvelope.parse(stream)
        self.assertEqual(envelope.command, b'verack')
        self.assertEqual(envelope.payload, b'')
        msg = bytes.fromhex('f9beb4d976657273696f6e0000000000650000005f1a69d2721101000100000000000000bc8f5e5400000000010000000000000000000000000000000000ffffc61b6409208d010000000000000000000000000000000000ffffcb0071c0208d128035cbc97953f80f2f5361746f7368693a302e392e332fcf05050001')
        stream = BytesIO(msg)
        envelope = NetworkEnvelope.parse(stream)
        self.assertEqual(envelope.command, b'version')
        self.assertEqual(envelope.payload, msg[24:])

    def test_serialize(self):
        msg = bytes.fromhex('f9beb4d976657261636b000000000000000000005df6e0e2')
        stream = BytesIO(msg)
        envelope = NetworkEnvelope.parse(stream)
        self.assertEqual(envelope.serialize(), msg)
        msg = bytes.fromhex('f9beb4d976657273696f6e0000000000650000005f1a69d2721101000100000000000000bc8f5e5400000000010000000000000000000000000000000000ffffc61b6409208d010000000000000000000000000000000000ffffcb0071c0208d128035cbc97953f80f2f5361746f7368693a302e392e332fcf05050001')
        stream = BytesIO(msg)
        envelope = NetworkEnvelope.parse(stream)
        self.assertEqual(envelope.serialize(), msg)


# tag::source2[]
class VersionMessage:
    command = b'version'

    def __init__(self, version=70015, services=0, timestamp=None,
                 receiver_services=0,
                 receiver_ip=b'\x00\x00\x00\x00', receiver_port=8333,
                 sender_services=0,
                 sender_ip=b'\x00\x00\x00\x00', sender_port=8333,
                 nonce=None, user_agent=b'/programmingbitcoin:0.1/',
                 latest_block=0, relay=False):
        self.version = version
        self.services = services
        if timestamp is None:
            self.timestamp = int(time.time())
        else:
            self.timestamp = timestamp
        self.receiver_services = receiver_services
        self.receiver_ip = receiver_ip
        self.receiver_port = receiver_port
        self.sender_services = sender_services
        self.sender_ip = sender_ip
        self.sender_port = sender_port
        if nonce is None:
            self.nonce = int_to_little_endian(randint(0, 2**64), 8)
        else:
            self.nonce = nonce
        self.user_agent = user_agent
        self.latest_block = latest_block
        self.relay = relay
    # end::source2[]

    def serialize(self):
        '''Serializuj ten komunikat, aby wysłać go przez sieć'''
        # wersja - 4 bajty, little endian
        # usługi 8 bajtów, little endian
        # znacznik czasu 8 bajtów, little endian
        # wersja - 8 bajty, little endian
        # IPV4 to 10 bajtów 00 i 2 bajty FF, a następnie ip odbiorcy
        # numer portu odbiorcy, to 2 bajty little-endian
        # usługi nadawcy, to 8 bajtów, little endian
        # IPV4 to 10 bajtów 00 i 2 bajty FF, a następnie ip nadawcy
        # numer portu odbiorcy, to 2 bajty little-endian
        # wartość nonce, to 8 bajtów
        # useragent, to łańcuch o zmiennej długości, a więc najpierw varint
        # ostatni blok, to 4 bajty, little endian
        # flaga relay (przekazywanie), to 00 dla fałszu i 01 dla prawdy
        raise NotImplementedError


class VersionMessageTest(TestCase):

    def test_serialize(self):
        v = VersionMessage(timestamp=0, nonce=b'\x00' * 8)
        self.assertEqual(v.serialize().hex(), '7f11010000000000000000000000000000000000000000000000000000000000000000000000ffff00000000208d000000000000000000000000000000000000ffff00000000208d0000000000000000182f70726f6772616d6d696e67626974636f696e3a302e312f0000000000')


# tag::source3[]
class VerAckMessage:
    command = b'verack'

    def __init__(self):
        pass

    @classmethod
    def parse(cls, s):
        return cls()

    def serialize(self):
        return b''
# end::source3[]


class PingMessage:
    command = b'ping'

    def __init__(self, nonce):
        self.nonce = nonce

    @classmethod
    def parse(cls, s):
        nonce = s.read(8)
        return cls(nonce)

    def serialize(self):
        return self.nonce


class PongMessage:
    command = b'pong'

    def __init__(self, nonce):
        self.nonce = nonce

    def parse(cls, s):
        nonce = s.read(8)
        return cls(nonce)

    def serialize(self):
        return self.nonce


# tag::source5[]
class GetHeadersMessage:
    command = b'getheaders'

    def __init__(self, version=70015, num_hashes=1, 
        start_block=None, end_block=None):
        self.version = version
        self.num_hashes = num_hashes  # <1>
        if start_block is None:  # <2>
            raise RuntimeError('wymagany blok początkowy')
        self.start_block = start_block
        if end_block is None:
            self.end_block = b'\x00' * 32  # <3>
        else:
            self.end_block = end_block
    # end::source5[]

    def serialize(self):
        '''Serializuj ten komunikat, aby wysłać go przez sieć'''
        # wersja protokołu, to 4 bajty, little endian
        # liczba skrótów, to varint
        # blok początkowy, to 4 bajty, little endian
        # blok końcowy, to 4 bajty, little endian
        raise NotImplementedError


class GetHeadersMessageTest(TestCase):

    def test_serialize(self):
        block_hex = '0000000000000000001237f46acddf58578a37e213d2a6edc4884a2fcad05ba3'
        gh = GetHeadersMessage(start_block=bytes.fromhex(block_hex))
        self.assertEqual(gh.serialize().hex(), '7f11010001a35bd0ca2f4a88c4eda6d213e2378a5758dfcd6af437120000000000000000000000000000000000000000000000000000000000000000000000000000000000')


# tag::source6[]
class HeadersMessage:
    command = b'headers'

    def __init__(self, blocks):
        self.blocks = blocks

    @classmethod
    def parse(cls, stream):
        num_headers = read_varint(stream)
        blocks = []
        for _ in range(num_headers):
            blocks.append(Block.parse(stream))  # <1>
            num_txs = read_varint(stream)  # <2>
            if num_txs != 0:  # <3>
                raise RuntimeError('niezerowa liczba transakcji')
        return cls(blocks)
    # end::source6[]


class HeadersMessageTest(TestCase):

    def test_parse(self):
        hex_msg = '0200000020df3b053dc46f162a9b00c7f0d5124e2676d47bbe7c5d0793a500000000000000ef445fef2ed495c275892206ca533e7411907971013ab83e3b47bd0d692d14d4dc7c835b67d8001ac157e670000000002030eb2540c41025690160a1014c577061596e32e426b712c7ca00000000000000768b89f07044e6130ead292a3f51951adbd2202df447d98789339937fd006bd44880835b67d8001ade09204600'
        stream = BytesIO(bytes.fromhex(hex_msg))
        headers = HeadersMessage.parse(stream)
        self.assertEqual(len(headers.blocks), 2)
        for b in headers.blocks:
            self.assertEqual(b.__class__, Block)


# tag::source4[]
class SimpleNode:

    def __init__(self, host, port=None, testnet=False, logging=False):
        if port is None:
            if testnet:
                port = 18333
            else:
                port = 8333
        self.testnet = testnet
        self.logging = logging
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.stream = self.socket.makefile('rb', None)
    # end::source4[]

    def handshake(self):
        '''Uzgodnij komunikację z drugim węzłem.
        wyślij komunikat version i odbierz verack.'''
        # utwórz komunikat wersji
        # wyślij polecenie
        # poczekaj na komunikat verack
        raise NotImplementedError
    # tag::source4[]

    def send(self, message):  # <1>
        '''Wyślij komunikat do podłączonego węzła'''
        envelope = NetworkEnvelope(
            message.command, message.serialize(), testnet=self.testnet)
        if self.logging:
            print('wysyłam: {}'.format(envelope))
        self.socket.sendall(envelope.serialize())

    def read(self):  # <2>
        '''Odczytaj komunikat z gniazda'''
        envelope = NetworkEnvelope.parse(self.stream, testnet=self.testnet)
        if self.logging:
            print('odbieram: {}'.format(envelope))
        return envelope

    def wait_for(self, *message_classes):  # <3>
        '''Czekaj na jeden z komunikatów z listy'''
        command = None
        command_to_class = {m.command: m for m in message_classes}
        while command not in command_to_class.keys():
            envelope = self.read()
            command = envelope.command
            if command == VersionMessage.command:
                self.send(VerAckMessage())
            elif command == PingMessage.command:
                self.send(PongMessage(envelope.payload))
        return command_to_class[command].parse(envelope.stream())
# end::source4[]


class SimpleNodeTest(TestCase):

    def test_handshake(self):
        node = SimpleNode('testnet.programmingbitcoin.com', testnet=True)
        node.handshake()
