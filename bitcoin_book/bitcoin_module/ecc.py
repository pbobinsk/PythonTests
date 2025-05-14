
import hashlib
import hmac

from io import BytesIO

from bitcoin_module.helper import encode_base58_checksum, hash160


# Zaimportuj funkcję encode z Twojego działającego modułu Bech32 (Sipy)
try:
    # Załóżmy, że plik Sipy nazwałeś bech32_sipa.py
    # i interesuje nas funkcja 'encode' zdefiniowana na końcu tego pliku
    from bitcoin_module.bech32_sipa import encode as sipa_bech32_segwit_encode 
    print("--- Zaimportowano 'encode' jako 'sipa_bech32_segwit_encode' z bech32_sipa.py ---")
except ImportError:
    print("BŁĄD: Nie można zaimportować funkcji 'encode' z 'bech32_sipa.py'.")
    print("Upewnij się, że plik 'bech32_sipa.py' (z implementacją Sipy) jest w tym samym katalogu.")
    exit()

class FieldElement:

    def __init__(self, num, prime):
        if num >= prime or num < 0:
            error = 'Liczba {} nie należy do zakresu od 0 do {}'.format(
                num, prime - 1)
            raise ValueError(error)
        self.num = num
        self.prime = prime

    def __repr__(self):
        return 'FieldElement_{}({})'.format(self.prime, self.num)

    def __eq__(self, other):
        if other is None:
            return False
        return self.num == other.num and self.prime == other.prime

    def __ne__(self, other):
        # Powinna być to odwrotność operatora ==
        return not (self == other)

    def __add__(self, other):
        if self.prime != other.prime:
            raise TypeError('Nie można dodać dwóch liczb z różnych ciał')
        # self.num i other.num to wartość
        # self.prime to wartość do operacji modulo
        num = (self.num + other.num) % self.prime
        # Zwracamy element tej samej klasy
        return self.__class__(num, self.prime)

    def __sub__(self, other):
        if self.prime != other.prime:
            raise TypeError('Nie można odejmować dwóch liczb z różnych ciał')
        # self.num i other.num to wartość
        # self.prime to wartość do operacji modulo
        num = (self.num - other.num) % self.prime
        # Zwracamy element tej samej klasy
        return self.__class__(num, self.prime)

    def __mul__(self, other):
        if self.prime != other.prime:
            raise TypeError('Nie można mnożyć dwóch liczb z różnych ciał')
        # self.num i other.num to wartość
        # self.prime to wartość do operacji modulo
        num = (self.num * other.num) % self.prime
        # Zwracamy element tej samej klasy
        return self.__class__(num, self.prime)

    def __pow__(self, exponent):
        n = exponent % (self.prime - 1)
        num = pow(self.num, n, self.prime)
        return self.__class__(num, self.prime)

    def __truediv__(self, other):
        if self.prime != other.prime:
            raise TypeError('Nie można dzielić dwóch liczb z różnych ciał')
        # self.num i other.num to wartość
        # self.prime to wartość do operacji modulo
        # Wykorzystaj małe twierdzenie Fermata:
        # self.num**(p-1) % p == 1
        # Czyli:
        # 1/n == pow(n, p-2, p)
        num = (self.num * pow(other.num, self.prime - 2, self.prime)) % self.prime
        # Zwracamy element tej samej klasy
        return self.__class__(num, self.prime)

    def __rmul__(self, coefficient):
        num = (self.num * coefficient) % self.prime
        return self.__class__(num=num, prime=self.prime)


# tag::source1[]
class Point:

    def __init__(self, x, y, a, b):
        self.a = a
        self.b = b
        self.x = x
        self.y = y
        if self.x is None and self.y is None:
            return
        if self.y**2 != self.x**3 + a * x + b:
            raise ValueError('({}, {}) nie leży na krzywej'.format(x, y))
    # end::source1[]

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y \
            and self.a == other.a and self.b == other.b

    def __ne__(self, other):
        # Powinna być to odwrotność operatora ==
        return not (self == other)

    def __repr__(self):
        if self.x is None:
            return 'Point(infinity)'
        elif isinstance(self.x, FieldElement):
            return 'Point({},{})_{}_{} FieldElement({})'.format(
                self.x.num, self.y.num, self.a.num, self.b.num, self.x.prime)
        else:
            return 'Point({},{})_{}_{}'.format(self.x, self.y, self.a, self.b)

    def __add__(self, other):
        if self.a != other.a or self.b != other.b:
            raise TypeError('Punkty {}, {} nie leżą na tej samej krzywej'.format(self, other))
        # Przypadek 0.0: self jest punktem w nieskończoności, zwróć other
        if self.x is None:
            return other
        # Przypadek 0.1: other jest punktem w nieskończoności, zwróć self
        if other.x is None:
            return self

        # Przypadek 1: self.x == other.x, self.y != other.y
        # Wynikiem jest punkt w nieskończoności
        if self.x == other.x and self.y != other.y:
            return self.__class__(None, None, self.a, self.b)

        # Przypadek 2: self.x ≠ other.x
        # Wzór (x3,y3)==(x1,y1)+(x2,y2)
        # s=(y2-y1)/(x2-x1)
        # x3=s**2-x1-x2
        # y3=s*(x1-x3)-y1
        if self.x != other.x:
            s = (other.y - self.y) / (other.x - self.x)
            x = s**2 - self.x - other.x
            y = s * (self.x - x) - self.y
            return self.__class__(x, y, self.a, self.b)

        # Przypadek 4: jeśli jesteśmy na stycznej do linii pionowej,
        # zwracamy punkt w nieskończoności
        # uwaga: zamiast zastanawiać się, czym jest 0 dla każdego typu,
        # użyjmy po prostu 0 * self.x
        if self == other and self.y == 0 * self.x:
            return self.__class__(None, None, self.a, self.b)

        # Przypadek 3: self == other
        # Wzór (x3,y3)=(x1,y1)+(x1,y1)
        # s=(3*x1**2+a)/(2*y1)
        # x3=s**2-2*x1
        # y3=s*(x1-x3)-y1
        if self == other:
            s = (3 * self.x**2 + self.a) / (2 * self.y)
            x = s**2 - 2 * self.x
            y = s * (self.x - x) - self.y
            return self.__class__(x, y, self.a, self.b)

    # tag::source3[]
    def __rmul__(self, coefficient):
        coef = coefficient
        current = self  # <1>
        result = self.__class__(None, None, self.a, self.b)  # <2>
        while coef:
            if coef & 1:  # <3>
                result += current
            current += current  # <4>
            coef >>= 1  # <5>
        return result
    # end::source3[]


# tag::source6[]
A = 0
B = 7
# end::source6[]
# tag::source4[]
P = 2**256 - 2**32 - 977
# end::source4[]
# tag::source9[]
N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
# end::source9[]


# tag::source5[]
class S256Field(FieldElement):

    def __init__(self, num, prime=None):
        super().__init__(num=num, prime=P)

    def __repr__(self):
        return '{:x}'.format(self.num).zfill(64)

    def sqrt(self):
        return self**((P + 1) // 4)


# tag::source7[]
class S256Point(Point):

    def __init__(self, x, y, a=None, b=None):
        a, b = S256Field(A), S256Field(B)
        if type(x) == int:
            super().__init__(x=S256Field(x), y=S256Field(y), a=a, b=b)
        else:
            super().__init__(x=x, y=y, a=a, b=b)  # <1>
    # end::source7[]

    def __repr__(self):
        if self.x is None:
            return 'S256Point(infinity)'
        else:
            return 'S256Point({}, {})'.format(self.x, self.y)

    # tag::source8[]
    def __rmul__(self, coefficient):
        coef = coefficient % N  # <1>
        return super().__rmul__(coef)
    # end::source8[]

    # tag::source12[]
    def verify(self, z, sig):
        s_inv = pow(sig.s, N - 2, N)  # <1>
        u = z * s_inv % N  # <2>
        v = sig.r * s_inv % N  # <3>
        total = u * G + v * self  # <4>
        return total.x.num == sig.r  # <5>
    # end::source12[]

    def sec(self, compressed=True):
        '''Zwraca postać binarną formatu SEC'''
        if compressed:
            if self.y.num % 2 == 0:
                return b'\x02' + self.x.num.to_bytes(32, 'big')
            else:
                return b'\x03' + self.x.num.to_bytes(32, 'big')
        else:
            return b'\x04' + self.x.num.to_bytes(32, 'big') + \
                self.y.num.to_bytes(32, 'big')
    # end::source1[]

    # tag::source5[]
    def hash160(self, compressed=True):
        return hash160(self.sec(compressed))

    def address(self, compressed=True, testnet=False):
        '''Zwraca łańcuch adresu'''
        h160 = self.hash160(compressed)
        if testnet:
            prefix = b'\x6f'
        else:
            prefix = b'\x00'
        return encode_base58_checksum(prefix + h160)
    # end::source5[]


    # --- NOWA METODA dla P2WPKH (Native SegWit / Bech32) ---
    def address_segwit_p2wpkh(self, testnet=False):
        '''Zwraca łańcuch adresu P2WPKH (Native SegWit, Bech32)'''
        if not BECH32_IMPLEMENTED:
            print("Nie można wygenerować adresu SegWit - brak biblioteki 'bech32'.")
            return None

        # Krok 1: Pobierz hash160 *skompresowanego* klucza publicznego (wymóg dla P2WPKH)
        h160_compressed = self.hash160(compressed=True) # To już są bajty

        # Krok 2: Ustaw wersję świadka (dla P2WPKH/P2WSH jest to 0)
        witness_version = 0

        # Krok 3: Określ Human-Readable Part (HRP)
        if testnet:
            hrp = 'tb' # HRP dla Testnet Bech32
        else:
            hrp = 'bc' # HRP dla Mainnet Bech32

        # Krok 4: Przygotuj dane do zakodowania
        # bech32.encode wymaga listy integerów: [wersja] + dane_przekonwertowane_na_5bit
        # Funkcja convertbits konwertuje bajty (8 bitów) na grupy 5-bitowe
        data_for_bech32 = bech32.convertbits(h160_compressed, 8, 5, pad=True)

        if data_for_bech32 is None:
             print("Błąd podczas konwersji bitów dla Bech32.")
             return None

        # Krok 5: Zakoduj używając Bech32
        # segwit_address = bech32.encode(hrp, [witness_version] + data_for_bech32)
        segwit_address = bech32.encode(hrp, witness_version, data_for_bech32)

        return segwit_address

    def generate_p2wpkh_address_from_privkey_secret(self, testnet=True):
        """
        Generuje adres P2WPKH (Native SegWit) na podstawie sekretu klucza prywatnego.
        """

        # 2. Uzyskaj punkt klucza publicznego (S256Point)
        public_key_point = self

        # 3. Uzyskaj skompresowany klucz publiczny w formacie SEC (bajty)
        compressed_pubkey_bytes = public_key_point.sec(compressed=True)
        # print(f"DEBUG: Skompresowany Klucz Publiczny (hex): {compressed_pubkey_bytes.hex()}")

        # 4. Oblicz HASH160 skompresowanego klucza publicznego (to jest program świadka)
        witness_program_bytes = hash160(compressed_pubkey_bytes)
        # print(f"DEBUG: Program Świadka (HASH160) (hex): {witness_program_bytes.hex()}")

        # 5. Ustaw wersję świadka (dla P2WPKH zawsze 0)
        witness_version = 0

        # 6. Ustaw Human-Readable Part (HRP)
        if testnet:
            hrp = 'tb'  # Dla Testnet
        else:
            hrp = 'bc'  # Dla Mainnet

        # ... (poprzednie kroki do witness_version i hrp) ...

        # 7. Przygotuj dane do zakodowania dla bech32.encode
        try:
            # Konwertuj 8-bitowe bajty programu świadka (HASH160) na 5-bitowe grupy integerów
            # To jest właśnie 'witprog' (witness program)
            converted_witness_program = bech32.convertbits(witness_program_bytes, 8, 5, True)
            if converted_witness_program is None:
                print("Błąd podczas konwersji bitów dla programu świadka.")
                return None
            
            # Użyj bech32.encode z trzema argumentami: hrp, wersja świadka, program świadka (5-bitowy)
            # To jest sygnatura, która zadziałała poprzednio w metodzie klasowej
            segwit_address = bech32.encode(hrp, witness_version, converted_witness_program) # <--- POPRAWKA TUTAJ

        except AttributeError as e:
            print(f"Błąd atrybutu w module bech32: {e}. Może inna nazwa funkcji lub sygnatura?")
            return None
        except TypeError as e: # Dodatkowa obsługa błędu typu, jeśli sygnatura jest nadal nie taka
            print(f"Błąd typu podczas kodowania Bech32 (prawdopodobnie zła liczba/typ argumentów): {e}")
            print(f"  HRP: {hrp} (typ: {type(hrp)})")
            print(f"  Witness Version: {witness_version} (typ: {type(witness_version)})")
            print(f"  Converted Witness Program: {converted_witness_program if 'converted_witness_program' in locals() else 'Error'} (typ: {type(converted_witness_program) if 'converted_witness_program' in locals() else 'Error'})")
            if 'converted_witness_program' in locals() and converted_witness_program is not None:
                print(f"    Pierwsze elementy converted_witness_program: {list(converted_witness_program)[:5]}")
            return None
        except Exception as e:
            print(f"Inny błąd podczas kodowania Bech32: {e}")
            return None

        return segwit_address



    # tag::source3[]
    @classmethod
    def parse(self, sec_bin):
        '''Zwraca obiekt Point dla binarnego formatu SEC (nie szesnastkowego)'''
        if sec_bin[0] == 4:  # <1>
            x = int.from_bytes(sec_bin[1:33], 'big')
            y = int.from_bytes(sec_bin[33:65], 'big')
            return S256Point(x=x, y=y)
        is_even = sec_bin[0] == 2  # <2>
        x = S256Field(int.from_bytes(sec_bin[1:], 'big'))
        # Prawa strona równania y^2 = x^3 + 7
        alpha = x**3 + S256Field(B)
        # Rozwiązujemy dla lewej strony
        beta = alpha.sqrt()  # <3>
        if beta.num % 2 == 0:  # <4>
            even_beta = beta
            odd_beta = S256Field(P - beta.num)
        else:
            even_beta = S256Field(P - beta.num)
            odd_beta = beta
        if is_even:
            return S256Point(x, even_beta)
        else:
            return S256Point(x, odd_beta)

# tag::source10[]
G = S256Point(
    0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
    0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)
# end::source10[]


# tag::source11[]
class Signature:

    def __init__(self, r, s):
        self.r = r
        self.s = s

    def __repr__(self):
        return 'Podpis({:x},{:x})'.format(self.r, self.s)
# end::source11[]
    def der(self):
        rbin = self.r.to_bytes(32, byteorder='big')
        # Usuwamy wszystkie zerowe bajty na początku
        rbin = rbin.lstrip(b'\x00')
        # Jeśli w rbin jest ustawiony najwyższy bit, dopisz \x00
        if rbin[0] & 0x80:
            rbin = b'\x00' + rbin
        result = bytes([2, len(rbin)]) + rbin  # <1>
        sbin = self.s.to_bytes(32, byteorder='big')
        # Usuwamy wszystkie zerowe bajty na początku
        sbin = sbin.lstrip(b'\x00')
        # Jeśli w sbin jest ustawiony najwyższy bit, dopisz \x00
        if sbin[0] & 0x80:
            sbin = b'\x00' + sbin
        result += bytes([2, len(sbin)]) + sbin
        return bytes([0x30, len(result)]) + result
    # end::source4[]

    @classmethod
    def parse(cls, signature_bin):
        s = BytesIO(signature_bin)
        compound = s.read(1)[0]
        if compound != 0x30:
            raise SyntaxError("Zły podpis")
        length = s.read(1)[0]
        if length + 2 != len(signature_bin):
            raise SyntaxError("Zła długość podpisu")
        marker = s.read(1)[0]
        if marker != 0x02:
            raise SyntaxError("Zły podpis")
        rlength = s.read(1)[0]
        r = int.from_bytes(s.read(rlength), 'big')
        marker = s.read(1)[0]
        if marker != 0x02:
            raise SyntaxError("Zły podpis")
        slength = s.read(1)[0]
        s = int.from_bytes(s.read(slength), 'big')
        if len(signature_bin) != 6 + rlength + slength:
            raise SyntaxError("Podpis za długi")
        return cls(r, s)


# tag::source13[]
class PrivateKey:

    def __init__(self, secret):
        self.secret = secret
        self.point = secret * G  # <1>

    def hex(self):
        return '{:x}'.format(self.secret).zfill(64)
    # end::source13[]

    # tag::source14[]
    def sign(self, z):
        k = self.deterministic_k(z)  # <1>
        r = (k * G).x.num
        k_inv = pow(k, N - 2, N)
        s = (z + r * self.secret) * k_inv % N
        if s > N / 2:
            s = N - s
        return Signature(r, s)

    def deterministic_k(self, z):
        k = b'\x00' * 32
        v = b'\x01' * 32
        if z > N:
            z -= N
        z_bytes = z.to_bytes(32, 'big')
        secret_bytes = self.secret.to_bytes(32, 'big')
        s256 = hashlib.sha256
        k = hmac.new(k, v + b'\x00' + secret_bytes + z_bytes, s256).digest()
        v = hmac.new(k, v, s256).digest()
        k = hmac.new(k, v + b'\x01' + secret_bytes + z_bytes, s256).digest()
        v = hmac.new(k, v, s256).digest()
        while True:
            v = hmac.new(k, v, s256).digest()
            candidate = int.from_bytes(v, 'big')
            if candidate >= 1 and candidate < N:
                return candidate  # <2>
            k = hmac.new(k, v + b'\x00', s256).digest()
            v = hmac.new(k, v, s256).digest()
    # end::source14[]
    def wif(self, compressed=True, testnet=False):
        secret_bytes = self.secret.to_bytes(32, 'big')
        if testnet:
            prefix = b'\xef'
        else:
            prefix = b'\x80'
        if compressed:
            suffix = b'\x01'
        else:
            suffix = b''
        return encode_base58_checksum(prefix + secret_bytes + suffix)


class PublicKey:
    def __init__(self, point):
        self.point = point  # Klucz publiczny jako punkt na krzywej

    def verify(self, z, signature):
        r, s = signature.r, signature.s
        if not (1 <= r < N and 1 <= s < N):
            return False  # Niepoprawny zakres

        s_inv = pow(s, N - 2, N)  # Odwrotność s modulo N
        u1 = z * s_inv % N
        u2 = r * s_inv % N
        point = u1 * G + u2 * self.point  # Weryfikacja ECDSA
        return point.x.num == r  # Sprawdzenie wartości r
    
    def __repr__(self):
        return f"PublicKey(x={hex(self.point.x.num)}, y={hex(self.point.y.num)})"


def generate_p2wpkh_address(secret_int, testnet=True):
    """
    Generuje adres P2WPKH (Native SegWit) na podstawie sekretu klucza prywatnego (liczby całkowitej).

    Args:
        secret_int (int): Sekret klucza prywatnego jako liczba całkowita.
        testnet (bool): True, jeśli adres ma być dla sieci Testnet, False dla Mainnet.

    Returns:
        str: Adres P2WPKH w formacie Bech32 lub None w przypadku błędu.
    """
    # 1. Utwórz obiekt PrivateKey z biblioteki Jimmy'ego Songa
    private_key = PrivateKey(secret=secret_int)

    # 2. Uzyskaj punkt klucza publicznego (S256Point)
    public_key_point = private_key.point

    # 3. Uzyskaj skompresowany klucz publiczny w formacie SEC (bajty)
    # Adresy P2WPKH ZAWSZE używają skompresowanego klucza publicznego.
    compressed_pubkey_bytes = public_key_point.sec(compressed=True)
    # print(f"DEBUG: Skompresowany Klucz Publiczny (hex): {compressed_pubkey_bytes.hex()}")

    # 4. Oblicz HASH160 skompresowanego klucza publicznego (to jest program świadka dla P2WPKH)
    # Wynik powinien być 20-bajtowy.
    witness_program_8bit_bytes = hash160(compressed_pubkey_bytes)
    # print(f"DEBUG: Program Świadka (HASH160) (hex): {witness_program_8bit_bytes.hex()}")
    # print(f"DEBUG: Długość Programu Świadka (HASH160): {len(witness_program_8bit_bytes)} bajtów")


    # 5. Ustaw wersję świadka (dla P2WPKH zawsze 0)
    witness_version = 0

    # 6. Ustaw Human-Readable Part (HRP)
    hrp = 'tb' if testnet else 'bc'

    # 7. Zakoduj używając funkcji 'encode' z modułu Sipy (bech32_sipa.py)
    # Ta funkcja oczekuje: hrp (string), witver (int), witprog (sekwencja intów reprezentujących bajty, np. obiekt bytes)
    try:
        segwit_address = sipa_bech32_segwit_encode(hrp, witness_version, witness_program_8bit_bytes)
        if segwit_address is None:
            print("BŁĄD: Kodowanie Bech32 zwróciło None (prawdopodobnie niepoprawne dane wejściowe dla wewnętrznych walidacji).")
            print(f"  HRP: {hrp}, Wersja: {witness_version}, Długość Programu: {len(witness_program_8bit_bytes)}")
            return None
    except Exception as e:
        print(f"BŁĄD podczas kodowania Bech32 (sipa_bech32_segwit_encode): {e}")
        return None

    return segwit_address

