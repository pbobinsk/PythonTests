
import hashlib
import hmac


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
# end::source5[]


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

