from unittest import TestSuite, TextTestRunner, TestLoader, TestCase

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

    def test_rmul(self):
        a = FieldElement(24, 31)
        b = 2
        self.assertEqual(b * a, a + a)

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

def run(test):
    suite = TestSuite()
    suite.addTest(test)
    TextTestRunner().run(suite)

def run_all(test_case_class):
    suite = TestLoader().loadTestsFromTestCase(test_case_class)
    TextTestRunner().run(suite)


if __name__ == "__main__":

    a = FieldElement(7, 13)
    b = FieldElement(6, 13)
    print('a = ',a)
    print('b = ',b)
    print('a == b ',a == b)
    print('a == a' ,a == a)
    print('a + b = ' ,a + b)
    print('a - b = ' ,a - b)
    print('a * b = ' ,a * b)
    print('a / b = ' ,a / b)
    

    run_all(FieldElementTest)