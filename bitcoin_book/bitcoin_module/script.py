from io import BytesIO
from logging import getLogger
from unittest import TestCase

from bitcoin_module.helper import (
    encode_varint,
    int_to_little_endian,
    little_endian_to_int,
    read_varint,
)
from bitcoin_module.op import (
    OP_CODE_FUNCTIONS,
    OP_CODE_NAMES,
)

def p2pkh_script(h160):
    '''Takes a hash160 and returns the p2pkh ScriptPubKey'''
    return Script([0x76, 0xa9, h160, 0x88, 0xac])

def p2sh_script(h160):
    '''Pobiera hash160 i zwraca p2sh ScriptPubKey'''
    return Script([0xa9, h160, 0x87])

LOGGER = getLogger(__name__)


def p2wpkh_script(h160_program_bytes): # Zmieniona nazwa argumentu dla jasności
    """Tworzy ScriptPubKey dla P2WPKH (OP_0 <20-byte program witness>)."""
    if not isinstance(h160_program_bytes, bytes) or len(h160_program_bytes) not in (20, 32): # P2WPKH to 20, P2WSH to 32
        raise ValueError("Program witness dla P2WPKH musi mieć 20 bajtów (lub 32 dla P2WSH).")
    # 0x00 to OP_0. Script([0x00, h160_program_bytes]) automatycznie doda pushdata.
    return Script([0x00, h160_program_bytes]) # Lub Script([OP_0, h160_program_bytes])

# tag::source1[]
class Script:

    def __init__(self, cmds=None):
        if cmds is None:
            self.cmds = []
        else:
            self.cmds = cmds  # <1>
    # end::source1[]

    def __repr__(self):
        result = []
        for cmd in self.cmds:
            if type(cmd) == int:
                if OP_CODE_NAMES.get(cmd):
                    name = OP_CODE_NAMES.get(cmd)
                else:
                    name = 'OP_[{}]'.format(cmd)
                result.append(name)
            else:
                result.append(cmd.hex())
        return ' '.join(result)

    # tag::source4[]
    def __add__(self, other):
        return Script(self.cmds + other.cmds)  # <1>
    # end::source4[]

    # tag::source2[]
    @classmethod
    def parse(cls, s):
        length = read_varint(s)  # <2>
        cmds = []
        count = 0
        while count < length:  # <3>
            current = s.read(1)  # <4>
            count += 1
            current_byte = current[0]  # <5>
            if current_byte >= 1 and current_byte <= 75:  # <6>
                n = current_byte
                cmds.append(s.read(n))
                count += n
            elif current_byte == 76:  # <7>
                data_length = little_endian_to_int(s.read(1))
                cmds.append(s.read(data_length))
                count += data_length + 1
            elif current_byte == 77:  # <8>
                data_length = little_endian_to_int(s.read(2))
                cmds.append(s.read(data_length))
                count += data_length + 2
            else:  # <9>
                op_code = current_byte
                cmds.append(op_code)
        if count != length:  # <10>
            raise SyntaxError('niepowodzenie skryptu interpretującego')
        return cls(cmds)
    # end::source2[]

    # tag::source3[]
    def raw_serialize(self):
        result = b''
        for cmd in self.cmds:
            if type(cmd) == int:  # <1>
                result += int_to_little_endian(cmd, 1)
            else:
                length = len(cmd)
                if length < 75:  # <2>
                    result += int_to_little_endian(length, 1)
                elif length > 75 and length < 0x100:  # <3>
                    result += int_to_little_endian(76, 1)
                    result += int_to_little_endian(length, 1)
                elif length >= 0x100 and length <= 520:  # <4>
                    result += int_to_little_endian(77, 1)
                    result += int_to_little_endian(length, 2)
                else:  # <5>
                    raise ValueError('za długie polecenie')
                result += cmd
        return result

    def serialize(self):
        result = self.raw_serialize()
        total = len(result)
        return encode_varint(total) + result  # <6>
    # end::source3[]

    # tag::source5[]
    def evaluate(self, z):
        LOGGER.info('evaluate start')
        cmds = self.cmds[:]  # <1>
        stack = []
        altstack = []
        while len(cmds) > 0:  # <2>
            cmd = cmds.pop(0)
            if type(cmd) == int:
                operation = OP_CODE_FUNCTIONS[cmd]  # <3>
                LOGGER.info('cmd '+str(cmd)+ ' hex '+str(hex(cmd))+' code '+ OP_CODE_NAMES[cmd])
                LOGGER.info('z '+str(z)+ ' hex '+str(hex(z)))
                
                if cmd in (99, 100):  # <4>
                    if not operation(stack, cmds):
                        LOGGER.info('zła op: {}'.format(OP_CODE_NAMES[cmd]))
                        return False
                elif cmd in (107, 108):  # <5>
                    if not operation(stack, altstack):
                        LOGGER.info('zła op: {}'.format(OP_CODE_NAMES[cmd]))
                        return False
                elif cmd in (172, 173, 174, 175):  # <6>
                    if not operation(stack, z):
                        LOGGER.info('zła op: {}'.format(OP_CODE_NAMES[cmd]))
                        return False
                else:
                    if not operation(stack):
                        LOGGER.info('zła op: {}'.format(OP_CODE_NAMES[cmd]))
                        return False
            else:
                LOGGER.info('cmd not int '+ str(cmd))
                stack.append(cmd)  # <7>
            LOGGER.info('stack '+ str(toints(stack)))
        if len(stack) == 0:
            return False  # <8>
        if stack.pop() == b'':
            return False  # <9>
        return True  # <10>
    # end::source5[]

    def is_p2pkh_script_pubkey(self):
        '''Sprawdza, czy jest to wzorzec: OP_DUP OP_HASH160 <20 bajtowy skrót> OP_EQUALVERIFY OP_CHECKSIG.'''
        return len(self.cmds) == 5 and self.cmds[0] == 0x76 \
            and self.cmds[1] == 0xa9 \
            and type(self.cmds[2]) == bytes and len(self.cmds[2]) == 20 \
            and self.cmds[3] == 0x88 and self.cmds[4] == 0xac

    def is_p2sh_script_pubkey(self):
        '''Sprawdza, czy jest to wzorzec: OP_HASH160 <20 bajtowy skrót> OP_EQUAL.'''
        return len(self.cmds) == 3 and self.cmds[0] == 0xa9 \
            and type(self.cmds[1]) == bytes and len(self.cmds[1]) == 20 \
            and self.cmds[2] == 0x87


def toints(s):
    return [int.from_bytes(b, byteorder='little') for b in s]