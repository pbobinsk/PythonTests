from field_element import FieldElement, run, run_all
from unittest import TestSuite, TextTestRunner, TestLoader, TestCase

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

    def __rmul__(self, coefficient):
        coef = coefficient
        current = self  
        result = self.__class__(None, None, self.a, self.b)  
        while coef:
            if coef & 1:  
                result += current
            current += current  
            coef >>= 1  
        return result
    


class PointTest(TestCase):

    def test_ne(self):
        a = Point(x=3, y=-7, a=5, b=7)
        b = Point(x=18, y=77, a=5, b=7)
        self.assertTrue(a != b)
        self.assertFalse(a != a)

    def test_on_curve(self):
        with self.assertRaises(ValueError):
            Point(x=-2, y=4, a=5, b=7)
        # nie powinno to zgłosić błędu
        Point(x=3, y=-7, a=5, b=7)
        Point(x=18, y=77, a=5, b=7)

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
        a = Point(x=-1, y=1, a=5, b=7)
        self.assertEqual(a + a, Point(x=18, y=-77, a=5, b=7))

if __name__ == "__main__":
    p1 = Point(-1, -1, 5, 7)
    # p2 = Point(-1, -2, 5, 7)
    print(p1)
    
    run_all(PointTest)