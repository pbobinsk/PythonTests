import hashlib, hmac
from bitcoin_field import N, G, PrivateKey, PublicKey

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


if __name__ == "__main__":
    

    # Proces generowania kluczy i podpisu w ECDSA (Elliptic Curve Digital Signature Algorithm):

    # Wiadomość i jej hash
    M = "Hello, Bitcoin!"
    h = int.from_bytes(hashlib.sha256(M.encode()).digest(), 'big')
    print('message M: ',M)
    print('hash h:',h)

    # Generowanie kluczy:
        # 1. Wybierz losowy skalar k (klucz prywatny) z zakresu [1, n-1] (gdzie n to rząd grupy punktu bazowego G).
    k = 0x1A2B3C4D5E6F7890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890
        # 2.Oblicz klucz publiczny K_pub = k * G (mnożenie punktu przez skalar).
    K_pub = k * G
    print('private key k: ','{:x}'.format(k))
    print('public key K_pub:',K_pub)

    # Podpisywanie wiadomości M (skrót h = Hash(M)):
        # 1. Wygeneruj losowy skalar k_e (efemeryczny, jednorazowy klucz) z [1, n-1].
    k_e = deterministic_k(k,h)
        # 2. Oblicz punkt R = k_e * G. Weź jego współrzędną x: r = R_x (mod n). Jeśli r=0, wróć do kroku 1.
    R = (k_e * G)
    r = R.x.num
        # 3. Oblicz s = (k_e^(-1) * (h + r * k_priv)) (mod n). (gdzie k_priv to klucz prywatny). Jeśli s=0, wróć do kroku 1.
    k_inv = pow(k_e, N - 2, N)
    s = (k_inv * (h + r * k)) % N
    if s > N / 2:
        s = N - s
        # 4. Podpis to para (r, s).
    print('signature (r,s): ({:x},{:x})'.format(r, s))

    # Weryfikacja podpisu (r, s) dla wiadomości M (skrót h = Hash(M)) i klucza publicznego K_pub:
        # 1. Sprawdź, czy r i s są w zakresie [1, n-1].
    if not (1 <= r < N and 1 <= s < N):
        raise ValueError('Niepoprawny zakres')

        # 2. Oblicz w = s^(-1) (mod n).
    s_inv = pow(s, N - 2, N) 
    w = s_inv
        # 3. Oblicz u1 = (h * w) (mod n).
    u1 = (h * w) % N  
        # 4. Oblicz u2 = (r * w) (mod n).
    u2 = (r * w) % N
        # 5. Oblicz punkt P_ver = (u1 * G) + (u2 * K_pub).
    P_ver = (u1 * G) + (u2 * K_pub)
        # 6. Jeśli P_ver == O (punkt w nieskończoności), podpis jest nieważny.
        # 7. Podpis jest ważny, jeśli P_ver_x (mod n) == r.
    valid = P_ver.x.num == r
    print('valid? ',valid)

    print('Wykorzystując klasy')

    priv = PrivateKey(k)
    signature = priv.sign(h)
    pub = PublicKey(priv.point)

    print(f"Podpis: (r={hex(signature.r)}, s={hex(signature.s)})")
    print(f"Klucz publiczny: ={pub}")

    is_valid = pub.verify(h, signature)
    print("Czy podpis jest poprawny?", is_valid)



