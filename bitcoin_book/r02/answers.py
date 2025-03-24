'''
# tag::exercise1[]
==== Ćwiczenie 1

Określ, które z następujących punktów leżą na krzywej __y__^2^ = __x__^3^ + 5__x__ + 7:

++++
<ul class="simplelist">
<li>(2,4), (–1,–1), (18,77), (5,7)</li>
</ul>
++++

# end::exercise1[]
# tag::answer1[]
>>> def on_curve(x, y):
...     return y**2 == x**3 + 5*x + 7
>>> print(on_curve(2,4))
False
>>> print(on_curve(-1,-1))
True
>>> print(on_curve(18,77))
True
>>> print(on_curve(5,7))
False

# end::answer1[]
# tag::exercise4[]
==== Ćwiczenie 4

Dla krzywej __y__^2^ = __x__^3^ + 5__x__ + 7 oblicz wynik dodawania punktów: (2,5) + (–1,–1).
# end::exercise4[]
# tag::answer4[]
>>> x1, y1 = 2, 5
>>> x2, y2 = -1, -1
>>> s = (y2 - y1) / (x2 - x1)
>>> x3 = s**2 - x1 - x2
>>> y3 = s * (x1 - x3) - y1
>>> print(x3, y3)
3.0 -7.0

# end::answer4[]
# tag::exercise6[]
==== Ćwiczenie 6

Dla krzywej __y__^2^ = __x__^3^ + 5__x__ + 7 oblicz wynik dodawania punktów: (–1,–1) + (–1,–1).
# end::exercise6[]
# tag::answer6[]
>>> a, x1, y1 = 5, -1, -1
>>> s = (3 * x1**2 + a) / (2 * y1)
>>> x3 = s**2 - 2*x1
>>> y3 = s*(x1-x3)-y1
>>> print(x3,y3)
18.0 77.0

# end::answer6[]
'''


from unittest import TestCase

from ecc import Point


'''
# tag::exercise2[]
==== Ćwiczenie 2

Napisz metodę `__ne__` dla klasy `Point`.
# end::exercise2[]
'''


# tag::answer2[]
def __ne__(self, other):
    return not (self == other)
# end::answer2[]


'''
# tag::exercise3[]
==== Ćwiczenie 3

Uwzględnij przypadek, w którym dwa punkty są elementami odwrotnymi dodawania (tzn. mają tę samą wartość `x`, ale inną wartość `y`, czego rezultatem jest linia pionowa). Wynikiem dodawania takich punktów powinien być punkt w nieskończoności.
# end::exercise3[]
# tag::exercise5[]
==== Ćwiczenie 5

Napisz metodę `__add__`, gdzie __x__~1~ ≠ __x__~2~.
# end::exercise5[]
# tag::exercise7[]
==== Ćwiczenie 7

Napisz metodę `__add__` uwzględniającą przypadek __P__~1~ = __P__~2~.
# end::exercise7[]
'''


def __add__(self, other):
    if self.a != other.a or self.b != other.b:
        raise TypeError
    if self.x is None:
        return other
    if other.x is None:
        return self
    # tag::answer3[]
    if self.x == other.x and self.y != other.y:
        return self.__class__(None, None, self.a, self.b)
    # end::answer3[]
    # tag::answer5[]
    if self.x != other.x:
        s = (other.y - self.y) / (other.x - self.x)
        x = s**2 - self.x - other.x
        y = s * (self.x - x) - self.y
        return self.__class__(x, y, self.a, self.b)
    # end::answer5[]
    if self == other and self.y == 0 * self.x:
        return self.__class__(None, None, self.a, self.b)
    # tag::answer7[]
    if self == other:
        s = (3 * self.x**2 + self.a) / (2 * self.y)
        x = s**2 - 2 * self.x
        y = s * (self.x - x) - self.y
        return self.__class__(x, y, self.a, self.b)
    # end::answer7[]


class ChapterTest(TestCase):

    def test_apply(self):
        Point.__ne__ = __ne__
        Point.__add__ = __add__
