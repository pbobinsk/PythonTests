a = {'a': 1, 'b' : '2', 'c' :3, 'd' : 4}

print(a)

b = {k:v for (v,k) in a.items()}

print(b)

import collections.abc

print(isinstance((), collections.abc.Sequence))
