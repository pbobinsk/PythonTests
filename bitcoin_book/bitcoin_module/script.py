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

# wypisywanie skryptu w pełni, na potrzebu prezentacji

    
    # Słownik z nazwami opcodów potrzebny dla `repr_all`
    OP_CODE_NAMES_ALL = {
        0: 'OP_0', 76: 'OP_PUSHDATA1', 77: 'OP_PUSHDATA2', 78: 'OP_PUSHDATA4',
        79: 'OP_1NEGATE', 81: 'OP_1', 82: 'OP_2', 83: 'OP_3', 84: 'OP_4', 85: 'OP_5',
        86: 'OP_6', 87: 'OP_7', 88: 'OP_8', 89: 'OP_9', 90: 'OP_10', 91: 'OP_11',
        92: 'OP_12', 93: 'OP_13', 94: 'OP_14', 95: 'OP_15', 96: 'OP_16', 97: 'OP_NOP',
        99: 'OP_IF', 100: 'OP_NOTIF', 103: 'OP_ELSE', 104: 'OP_ENDIF', 105: 'OP_VERIFY',
        106: 'OP_RETURN', 107: 'OP_TOALTSTACK', 108: 'OP_FROMALTSTACK', 
        110: 'OP_2DUP', 115: 'OP_IFDUP',
        116: 'OP_DEPTH', 117: 'OP_DROP', 118: 'OP_DUP', 119: 'OP_NIP', 120: 'OP_OVER',
        121: 'OP_PICK', 122: 'OP_ROLL', 123: 'OP_ROT', 124: 'OP_SWAP', 125: 'OP_TUCK',
        130: 'OP_SIZE', 135: 'OP_EQUAL', 136: 'OP_EQUALVERIFY', 139: 'OP_1ADD',
        140: 'OP_1SUB', 143: 'OP_NEGATE', 144: 'OP_ABS', 145: 'OP_NOT',
        146: 'OP_0NOTEQUAL', 147: 'OP_ADD', 148: 'OP_SUB', 154: 'OP_BOOLAND',
        155: 'OP_BOOLOR', 156: 'OP_NUMEQUAL', 157: 'OP_NUMEQUALVERIFY',
        158: 'OP_NUMNOTEQUAL', 159: 'OP_LESSTHAN', 160: 'OP_GREATERTHAN',
        161: 'OP_LESSTHANOREQUAL', 162: 'OP_GREATERTHANOREQUAL', 163: 'OP_MIN',
        164: 'OP_MAX', 165: 'OP_WITHIN', 166: 'OP_RIPEMD160', 167: 'OP_SHA1',
        168: 'OP_SHA256', 169: 'OP_HASH160', 170: 'OP_HASH256', 172: 'OP_CHECKSIG',
        173: 'OP_CHECKSIGVERIFY', 174: 'OP_CHECKMULTISIG', 175: 'OP_CHECKMULTISIGVERIFY',
        176: 'OP_NOP1', 177: 'OP_CHECKLOCKTIMEVERIFY', 178: 'OP_CHECKSEQUENCEVERIFY',
        179: 'OP_NOP4', 180: 'OP_NOP5', 181: 'OP_NOP6', 182: 'OP_NOP7', 183: 'OP_NOP8',
        184: 'OP_NOP9', 185: 'OP_NOP10',
    }
    # Dodajemy dynamicznie nazwy dla OP_PUSHBYTES_1 do OP_PUSHBYTES_75
    for i in range(1, 76):
        OP_CODE_NAMES_ALL[i] = f'OP_PUSHBYTES_{i}'


    @classmethod
    def parse_all(cls, s):
        """
        Parsuje strumień i tworzy obiekt Script, zachowując
        każdy opcode, w tym OP_PUSHBYTES, jako osobny element w liście cmds.
        Jest to wersja "debugowa", naśladująca Blockstream.info.
        """
        length = read_varint(s)
        cmds = []
        count = 0
        while count < length:
            current = s.read(1)
            count += 1
            current_byte = current[0]
            
            # Dla wszystkich opcodów typu PUSH...
            if 1 <= current_byte <= 75:  # OP_PUSHBYTES_N
                # ...najpierw dodaj sam opcode jako int...
                cmds.append(current_byte) 
                # ...a potem dodaj dane jako bytes
                n = current_byte
                cmds.append(s.read(n))
                count += n
            elif current_byte == 76:  # OP_PUSHDATA1
                cmds.append(current_byte)
                data_length = little_endian_to_int(s.read(1))
                cmds.append(s.read(data_length))
                count += data_length + 1
            elif current_byte == 77:  # OP_PUSHDATA2
                cmds.append(current_byte)
                data_length = little_endian_to_int(s.read(2))
                cmds.append(s.read(data_length))
                count += data_length + 2
            # OP_PUSHDATA4 (0x4e lub 78) nie jest w oryginalnym kodzie, ale warto dodać
            elif current_byte == 78: # OP_PUSHDATA4
                cmds.append(current_byte)
                data_length = little_endian_to_int(s.read(4))
                cmds.append(s.read(data_length))
                count += data_length + 4
            else:
                # Dla wszystkich innych opcodów, po prostu dodaj ich wartość int
                op_code = current_byte
                cmds.append(op_code)
                
        if count != length:
            raise SyntaxError('niepowodzenie skryptu interpretującego')
        
        # Zwróć nowy obiekt Script z tą szczegółową listą komend
        return cls(cmds)

    def repr_all(self):
        """
        Zwraca reprezentację stringową skryptu, która pokazuje każdy
        opcode, w tym OP_PUSHBYTES. Naśladuje Blockstream.info.
        """
        result = []
        for cmd in self.cmds:
            if isinstance(cmd, int):
                # Jeśli element jest liczbą, to jest to opcode
                if cmd in self.OP_CODE_NAMES_ALL:
                    name = self.OP_CODE_NAMES_ALL[cmd]
                else:
                    name = f'OP_[{cmd}]'
                result.append(name)
            elif isinstance(cmd, bytes):
                # Jeśli element jest bajtami, to są to dane
                result.append(cmd.hex())
            else:
                # Na wszelki wypadek, jeśli w liście jest coś innego
                result.append(str(cmd))
        return ' '.join(result) 
    
    def print_all(self):
        script_obj_standard = self
        print(f"Lista komend: {script_obj_standard.cmds}")
        print(f"Reprezentacja: {script_obj_standard}") # lub print(script_obj_standard.__repr__())
        print("\n--- Szczegółowe parsowanie (jak Blockstream.info) ---")
        # Musimy zresetować strumień, bo został już przeczytany
         
        # Użyj NOWEJ metody `parse_all`
        script_obj_all = self
        print(f"Lista komend: {script_obj_all.cmds}")
        # Użyj NOWEJ metody `repr_all` do wyświetlenia
        print(f"Reprezentacja: {script_obj_all.repr_all()}") 

    @staticmethod
    def print_all(script_hex):
        stream = BytesIO(script_hex)
        print("--- Standardowe parsowanie (logiczne) ---")
        # Użyj standardowej metody `parse`
        script_obj_standard = Script.parse(stream)
        print(f"Lista komend: {script_obj_standard.cmds}")
        print(f"Reprezentacja: {script_obj_standard}") # lub print(script_obj_standard.__repr__())
        print("\n--- Szczegółowe parsowanie (jak Blockstream.info) ---")
        # Musimy zresetować strumień, bo został już przeczytany
        stream.seek(0) 
        # Użyj NOWEJ metody `parse_all`
        script_obj_all = Script.parse_all(stream)
        print(f"Lista komend: {script_obj_all.cmds}")
        # Użyj NOWEJ metody `repr_all` do wyświetlenia
        print(f"Reprezentacja: {script_obj_all.repr_all()}") 

# koniec 


def toints(s):
    return [int.from_bytes(b, byteorder='little') for b in s]