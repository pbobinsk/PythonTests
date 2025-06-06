from field_element import FieldElement, run_all
from point import Point
import hashlib, hmac
from random import randint

A = 0
B = 7
P = 2**256 - 2**32 - 977
N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

class S256Field(FieldElement):

    def __init__(self, num, prime=None):
        super().__init__(num=num, prime=P)

    def __repr__(self):
        return '{:x}'.format(self.num).zfill(64)

    def sqrt(self):
        return self**((P + 1) // 4)


class S256Point(Point):

    def __init__(self, x, y, a=None, b=None):
        a, b = S256Field(A), S256Field(B)
        if type(x) == int:
            super().__init__(x=S256Field(x), y=S256Field(y), a=a, b=b)
        else:
            super().__init__(x=x, y=y, a=a, b=b) 


    def __repr__(self):
        if self.x is None:
            return 'S256Point(infinity)'
        else:
            return 'S256Point({}, {})'.format(self.x, self.y)

    def __rmul__(self, coefficient):
        coef = coefficient % N
        return super().__rmul__(coef)

    def verify(self, z, sig):
        s_inv = pow(sig.s, N - 2, N) 
        u = z * s_inv % N  
        v = sig.r * s_inv % N  
        total = u * G + v * self  
        return total.x.num == sig.r  

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


G = S256Point(
    0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
    0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)



from unittest import TestCase

class S256Test(TestCase):

    def test_order(self):
        point = N * G
        self.assertIsNone(point.x)

    def test_pubpoint(self):
        points = (
            # secret, x, y
            (7, 0x5cbdf0646e5db4eaa398f365f2ea7a0e3d419b7e0330e39ce92bddedcac4f9bc, 0x6aebca40ba255960a3178d6d861a54dba813d0b813fde7b5a5082628087264da),
            (1485, 0xc982196a7466fbbbb0e27a940b6af926c1a74d5ad07128c82824a11b5398afda, 0x7a91f9eae64438afb9ce6448a1c133db2d8fb9254e4546b6f001637d50901f55),
            (2**128, 0x8f68b9d2f63b5f339239c1ad981f162ee88c5678723ea3351b7b444c9ec4c0da, 0x662a9f2dba063986de1d90c2b6be215dbbea2cfe95510bfdf23cbf79501fff82),
            (2**240 + 2**31, 0x9577ff57c8234558f293df502ca4f09cbc65a6572c842b39b366f21717945116, 0x10b49c67fa9365ad7b90dab070be339a1daf9052373ec30ffae4f72d5e66d053),
        )

        for secret, x, y in points:
            point = S256Point(x, y)
            self.assertEqual(secret * G, point)

    def test_verify(self):
        point = S256Point(
            0x887387e452b8eacc4acfde10d9aaf7f6d9a0f975aabb10d006e4da568744d06c,
            0x61de6d95231cd89026e286df3b6ae4a894a3378e393e93a0f45b666329a0ae34)
        z = 0xec208baa0fc1c19f708a9ca96fdeff3ac3f230bb4a7ba4aede4942ad003c0f60
        r = 0xac8d1c87e51d0d441be8b3dd5b05c8795b48875dffe00b7ffcfac23010d3a395
        s = 0x68342ceff8935ededd102dd876ffd6ba72d6a427a3edb13d26eb0781cb423c4
        self.assertTrue(point.verify(z, Signature(r, s) ))
        z = 0x7c076ff316692a3d7eb3c3bb0f8b1488cf72e1afcd929e29307032997a838a3d
        r = 0xeff69ef2b1bd93a66ed5219add4fb51e11a840f404876325a1e8ffe0529a2c
        s = 0xc7207fee197d27c618aea621406f6bf5ef6fca38681d82b2f06fddbdce6feab6
        self.assertTrue(point.verify(z, Signature(r, s)))

    # def test_sec(self):
    #     coefficient = 999**3
    #     uncompressed = '049d5ca49670cbe4c3bfa84c96a8c87df086c6ea6a24ba6b809c9de234496808d56fa15cc7f3d38cda98dee2419f415b7513dde1301f8643cd9245aea7f3f911f9'
    #     compressed = '039d5ca49670cbe4c3bfa84c96a8c87df086c6ea6a24ba6b809c9de234496808d5'
    #     point = coefficient * G
    #     self.assertEqual(point.sec(compressed=False), bytes.fromhex(uncompressed))
    #     self.assertEqual(point.sec(compressed=True), bytes.fromhex(compressed))
    #     coefficient = 123
    #     uncompressed = '04a598a8030da6d86c6bc7f2f5144ea549d28211ea58faa70ebf4c1e665c1fe9b5204b5d6f84822c307e4b4a7140737aec23fc63b65b35f86a10026dbd2d864e6b'
    #     compressed = '03a598a8030da6d86c6bc7f2f5144ea549d28211ea58faa70ebf4c1e665c1fe9b5'
    #     point = coefficient * G
    #     self.assertEqual(point.sec(compressed=False), bytes.fromhex(uncompressed))
    #     self.assertEqual(point.sec(compressed=True), bytes.fromhex(compressed))
    #     coefficient = 42424242
    #     uncompressed = '04aee2e7d843f7430097859e2bc603abcc3274ff8169c1a469fee0f20614066f8e21ec53f40efac47ac1c5211b2123527e0e9b57ede790c4da1e72c91fb7da54a3'
    #     compressed = '03aee2e7d843f7430097859e2bc603abcc3274ff8169c1a469fee0f20614066f8e'
    #     point = coefficient * G
    #     self.assertEqual(point.sec(compressed=False), bytes.fromhex(uncompressed))
    #     self.assertEqual(point.sec(compressed=True), bytes.fromhex(compressed))

    # def test_address(self):
    #     secret = 888**3
    #     mainnet_address = '148dY81A9BmdpMhvYEVznrM45kWN32vSCN'
    #     testnet_address = 'mieaqB68xDCtbUBYFoUNcmZNwk74xcBfTP'
    #     point = secret * G
    #     self.assertEqual(
    #         point.address(compressed=True, testnet=False), mainnet_address)
    #     self.assertEqual(
    #         point.address(compressed=True, testnet=True), testnet_address)
    #     secret = 321
    #     mainnet_address = '1S6g2xBJSED7Qr9CYZib5f4PYVhHZiVfj'
    #     testnet_address = 'mfx3y63A7TfTtXKkv7Y6QzsPFY6QCBCXiP'
    #     point = secret * G
    #     self.assertEqual(
    #         point.address(compressed=False, testnet=False), mainnet_address)
    #     self.assertEqual(
    #         point.address(compressed=False, testnet=True), testnet_address)
    #     secret = 4242424242
    #     mainnet_address = '1226JSptcStqn4Yq9aAmNXdwdc2ixuH9nb'
    #     testnet_address = 'mgY3bVusRUL6ZB2Ss999CSrGVbdRwVpM8s'
    #     point = secret * G
    #     self.assertEqual(
    #         point.address(compressed=False, testnet=False), mainnet_address)
    #     self.assertEqual(
    #         point.address(compressed=False, testnet=True), testnet_address)


def deterministic_k(secret, z):
        k = b'\x00' * 32
        v = b'\x01' * 32
        if z > N:
            z -= N
        z_bytes = z.to_bytes(32, 'big')
        secret_bytes = secret.to_bytes(32, 'big')
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


class Signature:

    def __init__(self, r, s):
        self.r = r
        self.s = s

    def __repr__(self):
        return 'Podpis({:x},{:x})'.format(self.r, self.s)
    
    def der(self):
        rbin = self.r.to_bytes(32, byteorder='big')
        rbin = rbin.lstrip(b'\x00')
        if rbin[0] & 0x80:
            rbin = b'\x00' + rbin
        result = bytes([2, len(rbin)]) + rbin  # <1>
        sbin = self.s.to_bytes(32, byteorder='big')
        sbin = sbin.lstrip(b'\x00')
        if sbin[0] & 0x80:
            sbin = b'\x00' + sbin
        result += bytes([2, len(sbin)]) + sbin
        return bytes([0x30, len(result)]) + result    

class PrivateKey:

    def __init__(self, secret):
        self.secret = secret
        self.point = secret * G  # <1>

    def hex(self):
        return '{:x}'.format(self.secret).zfill(64)

    def sign(self, z):
        k = self.deterministic_k(z)
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


class SignatureTest(TestCase):

    def test_der(self):
            pass
    #     testcases = (
    #         (1, 2),
    #         (randint(0, 2**256), randint(0, 2**255)),
    #         (randint(0, 2**256), randint(0, 2**255)),
    #     )
    #     for r, s in testcases:
    #         sig = Signature(r, s)
    #         der = sig.der()
    #         sig2 = Signature.parse(der)
    #         self.assertEqual(sig2.r, r)
    #         self.assertEqual(sig2.s, s)


class PrivateKeyTest(TestCase):

    def test_sign(self):
        pk = PrivateKey(randint(0, N))
        z = randint(0, 2**256)
        sig = pk.sign(z)
        self.assertTrue(pk.point.verify(z, sig))
    
    # def test_wif(self):
    #     pk = PrivateKey(2**256 - 2**199)
    #     expected = 'L5oLkpV3aqBJ4BgssVAsax1iRa77G5CVYnv9adQ6Z87te7TyUdSC'
    #     self.assertEqual(pk.wif(compressed=True, testnet=False), expected)
    #     pk = PrivateKey(2**256 - 2**201)
    #     expected = '93XfLeifX7Jx7n7ELGMAf1SUR6f9kgQs8Xke8WStMwUtrDucMzn'
    #     self.assertEqual(pk.wif(compressed=False, testnet=True), expected)
    #     pk = PrivateKey(0x0dba685b4511dbd3d368e5c4358a1277de9486447af7b3604a69b8d9d8b7889d)
    #     expected = '5HvLFPDVgFZRK9cd4C5jcWki5Skz6fmKqi1GQJf5ZoMofid2Dty'
    #     self.assertEqual(pk.wif(compressed=False, testnet=False), expected)
    #     pk = PrivateKey(0x1cca23de92fd1862fb5b76e5f4f50eb082165e5191e116c18ed1a6b24be6a53f)
    #     expected = 'cNYfWuhDpbNM1JWc3c6JTrtrFVxU4AGhUKgw5f93NP2QaBqmxKkg'
    #     self.assertEqual(pk.wif(compressed=True, testnet=True), expected)




if __name__ == "__main__":

    run_all(S256Test)
    run_all(SignatureTest)
    run_all(PrivateKeyTest)



BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def hash160(s):
    '''sha256, a następnie ripemd160'''
    return hashlib.new('ripemd160', hashlib.sha256(s).digest()).digest()  

def hash256(s):
    '''dwukrotne obliczenia skrótu sha256'''
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

def encode_base58(s):
    count = 0
    for c in s:  
        if c == 0:
            count += 1
        else:
            break
    num = int.from_bytes(s, 'big')
    prefix = '1' * count
    result = ''
    while num > 0:  
        num, mod = divmod(num, 58)
        result = BASE58_ALPHABET[mod] + result
    return prefix + result  

def encode_base58_checksum(b):
    return encode_base58(b + hash256(b)[:4])

def decode_base58(s):
    num = 0
    for c in s:
        num *= 58
        num += BASE58_ALPHABET.index(c)
    combined = num.to_bytes(25, byteorder='big')
    checksum = combined[-4:]
    if hash256(combined[:-4])[:4] != checksum:
        raise ValueError('zły adres: {} {}'.format(checksum, hash256(combined[:-4])[:4]))
    return combined[1:-4]
