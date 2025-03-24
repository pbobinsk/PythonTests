from io import BytesIO
from logging import getLogger
from unittest import TestCase

from helper import (
    decode_base58,
    encode_varint,
    h160_to_p2pkh_address,
    h160_to_p2sh_address,
    int_to_little_endian,
    little_endian_to_int,
    read_varint,
    sha256,
)
from op import (
    op_equal,
    op_hash160,
    op_verify,
    OP_CODE_FUNCTIONS,
    OP_CODE_NAMES,
)


def p2pkh_script(h160):
    '''Pobiera hash160 i zwraca ScriptPubKey p2pkh'''
    return Script([0x76, 0xa9, h160, 0x88, 0xac])


def p2sh_script(h160):
    '''Pobiera hash160 i zwraca ScriptPubKey p2sh '''
    return Script([0xa9, h160, 0x87])


# tag::source1[]
def p2wpkh_script(h160):
    '''Pobiera skrót hash160 i zwraca ScriptPubKey p2wpkh'''
    return Script([0x00, h160])  # <1>
# end::source1[]


# tag::source4[]
def p2wsh_script(h256):
    '''Pobiera skrót hash160 i zwraca ScriptPubKey p2wsh'''
    return Script([0x00, h256])  # <1>
# end::source4[]


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

    def __add__(self, other):
        return Script(self.cmds + other.cmds)

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
        # utwórz kopię, ponieważ możemy potrzebować dodać coś do tej listy,
        # jeśli będziemy mieli RedeemScript
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
                    # operacje podpisywania; wymagają sig_hash do porównania
                    if not operation(stack, z):
                        LOGGER.info('zła op: {}'.format(OP_CODE_NAMES[cmd]))
                        return False
                else:
                    if not operation(stack):
                        LOGGER.info('zła op: {}'.format(OP_CODE_NAMES[cmd]))
                        return False
            else:
                # dodaj polecenie do stosu
                stack.append(cmd)
                # reguła p2sh. jeśli następne trzy polecenia to:
                # OP_HASH160 <20-bajtowy skrót> OP_EQUAL, to jest RedeemScript
                # OP_HASH160 == 0xa9 oraz OP_EQUAL == 0x87
                if len(cmds) == 3 and cmds[0] == 0xa9 \
                    and type(cmds[1]) == bytes and len(cmds[1]) == 20 \
                    and cmds[2] == 0x87:
                    redeem_script = encode_varint(len(cmd)) + cmd
                    # wykonujemy kolejne trzy kody operacji
                    cmds.pop()
                    h160 = cmds.pop()
                    cmds.pop()
                    if not op_hash160(stack):
                        return False
                    stack.append(h160)
                    if not op_equal(stack):
                        return False
                    # wynikiem końcowym powinna być wartość 1
                    if not op_verify(stack):
                        LOGGER.info('zły skrót p2sh h160')
                        return False
                    # skróty są zgodne! teraz dodaj RedeemScript
                    redeem_script = encode_varint(len(cmd)) + cmd
                    stream = BytesIO(redeem_script)
                    cmds.extend(Script.parse(stream).cmds)
                # reguła programu witness w wersji 0;
                # jeśli polecenia na stosie to: 0 <20-bajtowy skrót>, to jest p2wpkh
                # tag::source3[]
                if len(stack) == 2 and stack[0] == b'' and len(stack[1]) == 20:  # <1>
                    h160 = stack.pop()
                    stack.pop()
                    cmds.extend(witness)
                    cmds.extend(p2pkh_script(h160).cmds)
                # end::source3[]
                # reguła programu witness w wersji 0;
                # jeśli polecenia na stosie to: 0 <32-bajtowy skrót>, to jest p2wsh
                # tag::source6[]
                if len(stack) == 2 and stack[0] == b'' and len(stack[1]) == 32:
                    s256 = stack.pop()  # <1>
                    stack.pop()  # <2>
                    cmds.extend(witness[:-1])  # <3>
                    witness_script = witness[-1]  # <4>
                    if s256 != sha256(witness_script):  # <5>
                        print('niepoprawny skrót sha256 {} vs {}'.format
                            (s256.hex(), sha256(witness_script).hex()))
                        return False
                    stream = BytesIO(encode_varint(len(witness_script)) 
                        + witness_script)
                    witness_script_cmds = Script.parse(stream).cmds  # <6>
                    cmds.extend(witness_script_cmds)
                # end::source6[]
        if len(stack) == 0:
            return False
        if stack.pop() == b'':
            return False
        return True

    def is_p2pkh_script_pubkey(self):
        '''Sprawdza, czy jest to wzorzec: OP_DUP OP_HASH160 <20 bajtowy skrót> OP_EQUALVERIFY OP_CHECKSIG.'''
        # powinno być dokładnie 5 poleceń
        # OP_DUP (0x76), OP_HASH160 (0xa9), 20-bajtowy skrót, OP_EQUALVERIFY (0x88),
        # OP_CHECKSIG (0xac)
        return len(self.cmds) == 5 and self.cmds[0] == 0x76 \
            and self.cmds[1] == 0xa9 \
            and type(self.cmds[2]) == bytes and len(self.cmds[2]) == 20 \
            and self.cmds[3] == 0x88 and self.cmds[4] == 0xac

    def is_p2sh_script_pubkey(self):
        '''Sprawdza, czy jest to wzorzec: OP_HASH160 <20 bajtowy skrót> OP_EQUAL.'''
        # powinny być dokładnie 3 polecenia
        # OP_HASH160 (0xa9), 20-bajtowy skrót, OP_EQUAL (0x87)
        return len(self.cmds) == 3 and self.cmds[0] == 0xa9 \
            and type(self.cmds[1]) == bytes and len(self.cmds[1]) == 20 \
            and self.cmds[2] == 0x87

    # tag::source2[]
    def is_p2wpkh_script_pubkey(self):  # <2>
        return len(self.cmds) == 2 and self.cmds[0] == 0x00 \
            and type(self.cmds[1]) == bytes and len(self.cmds[1]) == 20
    # end::source2[]

    # tag::source5[]
    def is_p2wsh_script_pubkey(self):
        return len(self.cmds) == 2 and self.cmds[0] == 0x00 \
            and type(self.cmds[1]) == bytes and len(self.cmds[1]) == 32
    # end::source5[]

    def address(self, testnet=False):
        '''Zwraca adres odpowiadający skryptowi'''
        if self.is_p2pkh_script_pubkey():  # p2pkh
            # hash160 jest trzecim poleceniem
            h160 = self.cmds[2]
            # skonwertuj na adres p2pkh za pomocą h160_to_p2pkh_address (pamiętaj o testnecie)
            return h160_to_p2pkh_address(h160, testnet)
        elif self.is_p2sh_script_pubkey():  # p2sh
            # hash160 jest drugim poleceniem
            h160 = self.cmds[1]
            # skonwertuj na adres p2sh za pomocą h160_to_p2sh_address (pamiętaj o testnecie)
            return h160_to_p2sh_address(h160, testnet)
        raise ValueError('Unknown ScriptPubKey')


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

    def test_address(self):
        address_1 = '1BenRpVUFK65JFWcQSuHnJKzc4M8ZP8Eqa'
        h160 = decode_base58(address_1)
        p2pkh_script_pubkey = p2pkh_script(h160)
        self.assertEqual(p2pkh_script_pubkey.address(), address_1)
        address_2 = 'mrAjisaT4LXL5MzE81sfcDYKU3wqWSvf9q'
        self.assertEqual(p2pkh_script_pubkey.address(testnet=True), address_2)
        address_3 = '3CLoMMyuoDQTPRD3XYZtCvgvkadrAdvdXh'
        h160 = decode_base58(address_3)
        p2sh_script_pubkey = p2sh_script(h160)
        self.assertEqual(p2sh_script_pubkey.address(), address_3)
        address_4 = '2N3u1R6uwQfuobCqbCgBkpsgBxvr1tZpe7B'
        self.assertEqual(p2sh_script_pubkey.address(testnet=True), address_4)
