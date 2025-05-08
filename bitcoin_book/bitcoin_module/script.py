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


LOGGER = getLogger(__name__)


class Script:

    def __init__(self, cmds=None):
        if cmds is None:
            self.cmds = []
        else:
            self.cmds = cmds

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

    @classmethod
    def parse(cls, s):
        # pobierz długość całego pola
        length = read_varint(s)
        # zainicjuj tablicę cmds
        cmds = []
        # zainicjuj liczbę przeczytanych bajtów wartością 0
        count = 0
        # pętla, aż odczytamy liczbę bajtów z length
        while count < length:
            # pobierz bieżący bajt
            current = s.read(1)
            # zwiększ liczbę przeczytanych bajtów
            count += 1
            # przekonwertuj bieżący bajt na liczbę całkowitą
            current_byte = current[0]
            # jeśli bieżący bajt ma wartość od 1 do 75 włącznie
            if current_byte >= 1 and current_byte <= 75:
                # mamy zestaw polecenie; przypisz wartości n bieżący bajt
                n = current_byte
                # dodaj kolejne n bajtów jako polecenie
                cmds.append(s.read(n))
                # zwiększ wartość count o n
                count += n
            elif current_byte == 76:
                # op_pushdata1
                data_length = little_endian_to_int(s.read(1))
                cmds.append(s.read(data_length))
                count += data_length + 1
            elif current_byte == 77:
                # op_pushdata2
                data_length = little_endian_to_int(s.read(2))
                cmds.append(s.read(data_length))
                count += data_length + 2
            else:
                # mamy kod operacji; przypisz bieżący bajt zmiennej op_code
                op_code = current_byte
                # dodaj op_code do listy poleceń
                cmds.append(op_code)
        if count != length:
            raise SyntaxError('niepowodzenie skryptu interpretującego')
        return cls(cmds)

    def raw_serialize(self):
        # zainicjuj to, co później będziemy zwracać
        result = b''
        # przejrzyj przez wszystkie polecenia
        for cmd in self.cmds:
            # jeśli typem polecenia jest int, wiemy, że jest to kod operacji
            if type(cmd) == int:
                # zamień polecenie na jednobajtową liczbę całkowitą za pomocą int_to_little_endian
                result += int_to_little_endian(cmd, 1)
            else:
                # w przeciwnym razie jest to element danych
                # pobierz długość w bajtach
                length = len(cmd)
                # dla dużych długości, musimy użyć kodu operacji pushdata
                if length < 75:
                    # zamień długość na jednobajtową liczbę całkowitą
                    result += int_to_little_endian(length, 1)
                elif length > 75 and length < 0x100:
                    # 76 to pushdata1
                    result += int_to_little_endian(76, 1)
                    result += int_to_little_endian(length, 1)
                elif length >= 0x100 and length <= 520:
                    # 77 to pushdata2
                    result += int_to_little_endian(77, 1)
                    result += int_to_little_endian(length, 2)
                else:
                    raise ValueError('za długie polecenie')
                result += cmd
        return result

    def serialize(self):
        # pobierz surową serializację (bez wstawionej na początku długości)
        result = self.raw_serialize()
        # pobierz długość całości
        total = len(result)
        # zakoduj encode_varint całkowitą długość wyniku i wstaw na początek
        return encode_varint(total) + result

    def evaluate(self, z):
        # utwórz kopię, ponieważ możemy potrzebować dodać coś do tej listy, jeśli będziemy mieli
        # RedeemScript
        cmds = self.cmds[:]
        stack = []
        altstack = []
        while len(cmds) > 0:
            cmd = cmds.pop(0)
            if type(cmd) == int:
                # wykonaj działanie zależne od kodu operacji
                operation = OP_CODE_FUNCTIONS[cmd]
                if cmd in (99, 100):
                    # op_if/op_notif wymaga tablicy cmds
                    if not operation(stack, cmds):
                        LOGGER.info('zła op: {}'.format(OP_CODE_NAMES[cmd]))
                        return False
                elif cmd in (107, 108):
                    # op_toaltstack/op_fromaltstack wymaga altstack
                    if not operation(stack, altstack):
                        LOGGER.info('zła op: {}'.format(OP_CODE_NAMES[cmd]))
                        return False
                elif cmd in (172, 173, 174, 175):
                    # to operacje podpisywania; wymagają sig_hash do porównania
                    if not operation(stack, z):
                        LOGGER.info('zła op: {}'.format(OP_CODE_NAMES[cmd]))
                        return False
                else:
                    if not operation(stack):
                        LOGGER.info('zła op: {}'.format(OP_CODE_NAMES[cmd]))
                        return False
            else:
                # odłóż cmd na stos
                stack.append(cmd)
        if len(stack) == 0:
            return False
        if stack.pop() == b'':
            return False
        return True


class ScriptTest(TestCase):

    def test_parse(self):
        script_pubkey = BytesIO(bytes.fromhex('6a47304402207899531a52d59a6de200179928ca900254a36b8dff8bb75f5f5d71b1cdc26125022008b422690b8461cb52c3cc30330b23d574351872b7c361e9aae3649071c1a7160121035d5c93d9ac96881f19ba1f686f15f009ded7c62efe85a872e6a19b43c15a2937'))
        script = Script.parse(script_pubkey)
        want = bytes.fromhex('304402207899531a52d59a6de200179928ca900254a36b8dff8bb75f5f5d71b1cdc26125022008b422690b8461cb52c3cc30330b23d574351872b7c361e9aae3649071c1a71601')
        self.assertEqual(script.cmds[0].hex(), want.hex())
        want = bytes.fromhex('035d5c93d9ac96881f19ba1f686f15f009ded7c62efe85a872e6a19b43c15a2937')
        self.assertEqual(script.cmds[1], want)

    def test_serialize(self):
        want = '6a47304402207899531a52d59a6de200179928ca900254a36b8dff8bb75f5f5d71b1cdc26125022008b422690b8461cb52c3cc30330b23d574351872b7c361e9aae3649071c1a7160121035d5c93d9ac96881f19ba1f686f15f009ded7c62efe85a872e6a19b43c15a2937'
        script_pubkey = BytesIO(bytes.fromhex(want))
        script = Script.parse(script_pubkey)
        self.assertEqual(script.serialize().hex(), want)
