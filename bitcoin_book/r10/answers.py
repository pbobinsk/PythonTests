'''
# tag::exercise2[]
==== Ćwiczenie 2

Określ, co zawiera ten komunikat sieciowy:

----
f9beb4d976657261636b000000000000000000005df6e0e2
----
# end::exercise2[]
# tag::answer2[]
>>> from network import NetworkEnvelope
>>> from io import BytesIO
>>> message_hex = 'f9beb4d976657261636b000000000000000000005df6e0e2'
>>> stream = BytesIO(bytes.fromhex(message_hex))
>>> envelope = NetworkEnvelope.parse(stream)
>>> print(envelope.command)
b'verack'
>>> print(envelope.payload)
b''

# end::answer2[]
'''


from unittest import TestCase

from helper import (
    encode_varint,
    hash256,
    int_to_little_endian,
    little_endian_to_int,
)
from network import (
    GetHeadersMessage,
    NetworkEnvelope,
    SimpleNode,
    VersionMessage,
    VerAckMessage,
    NETWORK_MAGIC,
    TESTNET_NETWORK_MAGIC,
)


methods = []


'''
# tag::exercise1[]
==== Ćwiczenie 1

Napisz metodę `parse` dla klasy `NetworkEnvelope`.
# end::exercise1[]
'''


# tag::answer1[]
@classmethod
def parse(cls, s, testnet=False):
    magic = s.read(4)
    if magic == b'':
        raise IOError('Połączenie zresetowane!')
    if testnet:
        expected_magic = TESTNET_NETWORK_MAGIC
    else:
        expected_magic = NETWORK_MAGIC
    if magic != expected_magic:
        raise SyntaxError('Nieprawidłowa wartość {} vs {}'.format(magic.hex(), 
          expected_magic.hex()))
    command = s.read(12)
    command = command.strip(b'\x00')
    payload_length = little_endian_to_int(s.read(4))
    checksum = s.read(4)
    payload = s.read(payload_length)
    calculated_checksum = hash256(payload)[:4]
    if calculated_checksum != checksum:
        raise IOError('nieprawidłowa suma kontrolna')
    return cls(command, payload, testnet=testnet)
# end::answer1[]


'''
# tag::exercise3[]
==== Ćwiczenie 3

Napisz metodę `serialize` dla klasy `NetworkEnvelope`.
# end::exercise3[]
'''


# tag::answer3[]
def serialize(self):
    result = self.magic
    result += self.command + b'\x00' * (12 - len(self.command))
    result += int_to_little_endian(len(self.payload), 4)
    result += hash256(self.payload)[:4]
    result += self.payload
    return result
# end::answer3[]


methods.append(serialize)


'''
# tag::exercise4[]
==== Ćwiczenie 4

Napisz metodę `serialize` dla klasy `VersionMessage`.
# end::exercise4[]
'''


# tag::answer4[]
def serialize(self):
    result = int_to_little_endian(self.version, 4)
    result += int_to_little_endian(self.services, 8)
    result += int_to_little_endian(self.timestamp, 8)
    result += int_to_little_endian(self.receiver_services, 8)
    result += b'\x00' * 10 + b'\xff\xff' + self.receiver_ip
    result += self.receiver_port.to_bytes(2, 'big')
    result += int_to_little_endian(self.sender_services, 8)
    result += b'\x00' * 10 + b'\xff\xff' + self.sender_ip
    result += self.sender_port.to_bytes(2, 'big')
    result += self.nonce
    result += encode_varint(len(self.user_agent))
    result += self.user_agent
    result += int_to_little_endian(self.latest_block, 4)
    if self.relay:
        result += b'\x01'
    else:
        result += b'\x00'
    return result
# end::answer4[]


methods.append(serialize)


'''
# tag::exercise5[]
==== Ćwiczenie 5

Napisz metodę `handshake` dla klasy `SimpleNode`.
# end::exercise5[]
'''


# tag::answer5[]
def handshake(self):
    version = VersionMessage()
    self.send(version)
    self.wait_for(VerAckMessage)
# end::answer5[]


'''
# tag::exercise6[]
==== Ćwiczenie 6

Napisz metodę `serialize` dla klasy `GetHeadersMessage`.
# end::exercise6[]
'''


# tag::answer6[]
def serialize(self):
    result = int_to_little_endian(self.version, 4)
    result += encode_varint(self.num_hashes)
    result += self.start_block[::-1]
    result += self.end_block[::-1]
    return result
# end::answer6[]


methods.append(serialize)


class ChapterTest(TestCase):

    def test_apply(self):
        NetworkEnvelope.parse = parse
        NetworkEnvelope.serialize = methods[0]
        VersionMessage.serialize = methods[1]
        SimpleNode.handshake = handshake
        GetHeadersMessage.serialize = methods[2]
