from unittest import TestCase


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


class FieldElementTest(TestCase):

    def test_ne(self):
        a = FieldElement(2, 31)
        b = FieldElement(2, 31)
        c = FieldElement(15, 31)
        self.assertEqual(a, b)
        self.assertTrue(a != c)
        self.assertFalse(a != b)

    def test_add(self):
        a = FieldElement(2, 31)
        b = FieldElement(15, 31)
        self.assertEqual(a + b, FieldElement(17, 31))
        a = FieldElement(17, 31)
        b = FieldElement(21, 31)
        self.assertEqual(a + b, FieldElement(7, 31))

    def test_sub(self):
        a = FieldElement(29, 31)
        b = FieldElement(4, 31)
        self.assertEqual(a - b, FieldElement(25, 31))
        a = FieldElement(15, 31)
        b = FieldElement(30, 31)
        self.assertEqual(a - b, FieldElement(16, 31))

    def test_mul(self):
        a = FieldElement(24, 31)
        b = FieldElement(19, 31)
        self.assertEqual(a * b, FieldElement(22, 31))

    def test_pow(self):
        a = FieldElement(17, 31)
        self.assertEqual(a**3, FieldElement(15, 31))
        a = FieldElement(5, 31)
        b = FieldElement(18, 31)
        self.assertEqual(a**5 * b, FieldElement(16, 31))

    def test_div(self):
        a = FieldElement(3, 31)
        b = FieldElement(24, 31)
        self.assertEqual(a / b, FieldElement(4, 31))
        a = FieldElement(17, 31)
        self.assertEqual(a**-3, FieldElement(29, 31))
        a = FieldElement(4, 31)
        b = FieldElement(11, 31)
        self.assertEqual(a**-4 * b, FieldElement(13, 31))


# tag::source1[]
class Point:

    def __init__(self, x, y, a, b):
        self.a = a
        self.b = b
        self.x = x
        self.y = y
        # end::source1[]
        # tag::source2[]
        if self.x is None and self.y is None:  # <1>
            return
        # end::source2[]
        # tag::source1[]
        if self.y**2 != self.x**3 + a * x + b:  # <1>
            raise ValueError('({}, {}) nie leży na krzywej'.format(x, y))

    def __eq__(self, other):  # <2>
        return self.x == other.x and self.y == other.y \
            and self.a == other.a and self.b == other.b
    # end::source1[]

    def __ne__(self, other):
        # Powinna być to odwrotność operatora ==
        raise NotImplementedError

    def __repr__(self):
        if self.x is None:
            return 'Point(infinity)'
        else:
            return 'Point({},{})_{}_{}'.format(self.x, self.y, self.a, self.b)

    # tag::source3[]
    def __add__(self, other):  # <2>
        if self.a != other.a or self.b != other.b:
            raise TypeError('Punkty {}, {} nie leżą na tej samej krzywej'.format
            (self, other))

        if self.x is None:  # <3>
            return other
        if other.x is None:  # <4>
            return self
        # end::source3[]

        # Przypadek 1: self.x == other.x, self.y != other.y
        # Wynikiem jest punkt w nieskończoności

        # Przypadek 2: self.x ≠ other.x
        # Wzór (x3,y3)==(x1,y1)+(x2,y2)
        # s=(y2-y1)/(x2-x1)
        # x3=s**2-x1-x2
        # y3=s*(x1-x3)-y1

        # Przypadek 3: self == other
        # Wzór (x3,y3)=(x1,y1)+(x1,y1)
        # s=(3*x1**2+a)/(2*y1)
        # x3=s**2-2*x1
        # y3=s*(x1-x3)-y1

        raise NotImplementedError


class PointTest(TestCase):

    def test_ne(self):
        a = Point(x=3, y=-7, a=5, b=7)
        b = Point(x=18, y=77, a=5, b=7)
        self.assertTrue(a != b)
        self.assertFalse(a != a)

    def test_add0(self):
        a = Point(x=None, y=None, a=5, b=7)
        b = Point(x=2, y=5, a=5, b=7)
        c = Point(x=2, y=-5, a=5, b=7)
        self.assertEqual(a + b, b)
        self.assertEqual(b + a, b)
        self.assertEqual(b + c, a)

    def test_add1(self):
        a = Point(x=3, y=7, a=5, b=7)
        b = Point(x=-1, y=-1, a=5, b=7)
        self.assertEqual(a + b, Point(x=2, y=-5, a=5, b=7))

    def test_add2(self):
        a = Point(x=-1, y=-1, a=5, b=7)
        self.assertEqual(a + a, Point(x=18, y=77, a=5, b=7))
