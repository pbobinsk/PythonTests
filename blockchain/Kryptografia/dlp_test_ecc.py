# --- Przykład: Ilustracja Problemu Logarytmu Dyskretnego na Krzywych Eliptycznych (ECDLP) ---
# Założenia: Masz zdefiniowane klasy:
#   - S256Field(num): Element ciała F_p dla p z secp256k1
#   - S256Point(x, y): Punkt na krzywej secp256k1. Zakładamy, że x, y mogą być int lub S256Field.
#                      Jeśli x, y to None, to jest to punkt w nieskończoności.
#   - Stałą G: Punkt bazowy dla secp256k1 (obiekt S256Point)
#   - Zdefiniowaną operację mnożenia punktu przez skalar: `scalar * Point_object`
#     np. poprzez przeciążenie operatora __mul__ w klasie S256Point lub __rmul__ w klasie skalarnej.

# --- Symulacja implementacji (aby kod był uruchamialny koncepcyjnie) ---
# W rzeczywistym kodzie użyłbyś swojej implementacji.
# To jest tylko MOCKUP dla demonstracji.

class MockS256Field:
    def __init__(self, num, prime=None): # prime jest ignorowane w mocku
        self.num = num
    def __repr__(self):
        return f"FieldElement({self.num})"

class MockS256Point:
    def __init__(self, x, y, curve_a=None, curve_b=None): # parametry krzywej ignorowane w mocku
        if x is None: # Punkt w nieskończoności
            self.x_coord = None
            self.y_coord = None
        else:
            # Zakładamy, że x, y mogą być int lub MockS256Field
            self.x_coord = x.num if isinstance(x, MockS256Field) else x
            self.y_coord = y.num if isinstance(y, MockS256Field) else y

    def __rmul__(self, scalar): # Dla scalar * Point
        # BARDZO UPROSZCZONA "SYMULACJA" mnożenia, NIEPOPRAWNA KRYPTOGRAFICZNIE!
        # Służy tylko do zilustrowania, że coś się dzieje.
        # W rzeczywistości tu działałby algorytm double-and-add.
        if self.x_coord is None: return self # k * O = O
        # "Symulujemy" nowe współrzędne, aby nie były trywialne
        # W prawdziwym ECC, wynik byłby punktem na krzywej.
        # Używamy hasha, aby wynik był deterministyczny, ale "skomplikowany"
        import hashlib
        h_x = int(hashlib.sha256(f"x_coord_mul_{self.x_coord}_{scalar}".encode()).hexdigest(), 16) % (10**10) # Ograniczamy dla czytelności
        h_y = int(hashlib.sha256(f"y_coord_mul_{self.y_coord}_{scalar}".encode()).hexdigest(), 16) % (10**10)
        return MockS256Point(h_x, h_y)
        
    def __repr__(self):
        if self.x_coord is None:
            return "Point(infinity)"
        # Dla uproszczenia pokazujemy tylko liczby int
        x_val = self.x_coord.num if hasattr(self.x_coord, 'num') else self.x_coord
        y_val = self.y_coord.num if hasattr(self.y_coord, 'num') else self.y_coord
        return f"Point(x={x_val}, y={y_val})" # Skrócona reprezentacja

# Załóżmy, że G jest zdefiniowane gdzieś globalnie w Twoim kodzie
# Dla przykładu, użyjemy tu przykładowych wartości dla G
# W secp256k1, Gx i Gy to konkretne, bardzo duże liczby.
Gx_secp256k1_example = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy_secp256k1_example = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
# G = S256Point(Gx_secp256k1_example, Gy_secp256k1_example) # Twoja rzeczywista klasa
G = MockS256Point(12345, 67890) # Używamy mocka z prostszymi liczbami dla demonstracji

# Rząd grupy n dla secp256k1 (bardzo duża liczba pierwsza)
N_secp256k1 = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
# --- Koniec Mockup ---


def run_ecdlp_illustration():
    print("--- Przykład: Ilustracja Problemu Logarytmu Dyskretnego na Krzywych Eliptycznych (ECDLP) ---")

    # Klucz prywatny (skalar) - to jest to, co chcemy znaleźć w ECDLP
    # W praktyce jest to duża, losowo wybrana liczba z zakresu [1, n-1]
    private_key_scalar = 1800555111222333444555 # Przykładowy duży skalar
    # private_key_scalar = random.randint(1, N_secp256k1 -1) # Tak by to wyglądało w praktyce

    print(f"Punkt bazowy (Generator) G = {G}")
    print(f"Tajny skalar (klucz prywatny) k = {private_key_scalar}  <-- To jest 'x' w g^x")

    # 1. Łatwa operacja: Mnożenie punktu przez skalar (odpowiednik g^x)
    #    Public_Key_Point = private_key_scalar * G
    #    To jest operacja wykonywana do wygenerowania klucza publicznego.
    #    Użyj swojej implementacji mnożenia punktu przez skalar.
    
    # Zakładając, że masz przeciążony operator mnożenia dla skalar * Point
    public_key_point = private_key_scalar * G # Wywołanie twojej metody mnożenia
    
    print(f"Klucz publiczny (Punkt) P = k * G = {public_key_point}  <-- TO JEST ŁATWE do obliczenia")

    # 2. Trudna operacja: ECDLP
    #    Mając G i P (public_key_point), znaleźć private_key_scalar.
    print("\nProblem ECDLP:")
    print(f"  Dane: Punkt bazowy G = {G}")
    print(f"  Dane: Punkt publiczny P = {public_key_point}")
    print(f"  Zadanie: Znaleźć skalar k taki, że k * G = P.")
    print(f"  Odpowiedź (którą znamy, ale trudno ją obliczyć z G i P): k = {private_key_scalar}")
    print("  Dla krzywych używanych w kryptografii (np. secp256k1), znalezienie 'k' jest obliczeniowo niewykonalne,")
    print("  jeśli 'k' jest odpowiednio duże i losowe, a parametry krzywej są bezpieczne.")
    print("  Nie ma znanego efektywnego algorytmu ogólnego (jak np. sito dla faktoryzacji),")
    print("  który by to robił dla dowolnych krzywych eliptycznych.")

    print("\nDyskusja:")
    print(" - Mnożenie punktu G przez skalar 'k' (aby uzyskać P) jest wydajne (np. algorytm double-and-add).")
    print(" - Odwrotna operacja, znalezienie 'k' mając G i P, to ECDLP i jest trudne.")
    print(" - Bezpieczeństwo ECC (ECDH, ECDSA używane w Bitcoin, Ethereum) opiera się na tej trudności.")
    print("--------------------------------------------------------------------------------------\n")

import time


class MockFiniteFieldElement:
    def __init__(self, num, prime):
        if not isinstance(num, int) or not isinstance(prime, int):
            raise TypeError("Num i prime muszą być liczbami całkowitymi")
        self.num = num % prime
        self.prime = prime
    def __add__(self, other):
        if self.prime != other.prime: raise TypeError("Niezgodne ciała")
        return MockFiniteFieldElement((self.num + other.num) % self.prime, self.prime)
    def __sub__(self, other):
        if self.prime != other.prime: raise TypeError("Niezgodne ciała")
        return MockFiniteFieldElement((self.num - other.num + self.prime) % self.prime, self.prime)
    def __mul__(self, other):
        if isinstance(other, int): return MockFiniteFieldElement((self.num * other) % self.prime, self.prime)
        if self.prime != other.prime: raise TypeError("Niezgodne ciała")
        return MockFiniteFieldElement((self.num * other.num) % self.prime, self.prime)
    def __rmul__(self, other_int):
        if isinstance(other_int, int): return self.__mul__(other_int)
        raise TypeError("Mnożenie przez skalar obsługuje tylko int")
    def __pow__(self, exponent): return MockFiniteFieldElement(pow(self.num, exponent, self.prime), self.prime)
    def __truediv__(self, other):
        if self.prime != other.prime: raise TypeError("Niezgodne ciała")
        inv_other_num = pow(other.num, self.prime - 2, self.prime)
        return MockFiniteFieldElement((self.num * inv_other_num) % self.prime, self.prime)
    def __eq__(self, other): return isinstance(other, MockFiniteFieldElement) and self.num == other.num and self.prime == other.prime
    def __ne__(self, other): return not (self == other)
    def __repr__(self): return f"FE_{self.prime}({self.num})"
    def __hash__(self): return hash((self.num, self.prime))

class MockCurvePoint:
    def __init__(self, x_fe, y_fe, a_fe, b_fe):
        self.a = a_fe 
        self.b = b_fe 
        self.x = x_fe
        self.y = y_fe
        if self.x is None and self.y is None: return
        if not all(isinstance(fe, MockFiniteFieldElement) for fe in [self.x, self.y, self.a, self.b]): raise TypeError("Współrzędne i parametry krzywej muszą być elementami ciała skończonego.")
        if not (self.x.prime == self.y.prime == self.a.prime == self.b.prime): raise TypeError("Współrzędne i parametry krzywej muszą być z tego samego ciała.")
    def __add__(self, other):
        if self.a != other.a or self.b != other.b: raise TypeError("Punkty muszą być na tej samej krzywej")
        if self.x is None: return other
        if other.x is None: return self
        if self.x == other.x and (self.y + other.y == MockFiniteFieldElement(0, self.x.prime)): return MockCurvePoint(None, None, self.a, self.b)
        if self.x != other.x:
            s = (other.y - self.y) / (other.x - self.x)
            x3 = s * s - self.x - other.x
            y3 = s * (self.x - x3) - self.y
            return MockCurvePoint(x3, y3, self.a, self.b)
        if self == other:
            if self.y == MockFiniteFieldElement(0, self.x.prime): return MockCurvePoint(None, None, self.a, self.b)
            s_num = 3 * self.x * self.x + self.a
            s_den = 2 * self.y
            s = s_num / s_den
            x3 = s * s - 2 * self.x
            y3 = s * (self.x - x3) - self.y
            return MockCurvePoint(x3, y3, self.a, self.b)
        raise ValueError(f"Nieobsługiwany przypadek w dodawaniu punktów: self={self}, other={other}")
    def __rmul__(self, scalar_int):
        if not isinstance(scalar_int, int): raise TypeError("Skalar musi być liczbą całkowitą")
        if scalar_int < 0:
            neg_self = MockCurvePoint(self.x, MockFiniteFieldElement(0, self.x.prime) - self.y if self.y else None, self.a, self.b)
            return (-scalar_int) * neg_self
        if scalar_int == 0: return MockCurvePoint(None, None, self.a, self.b)
        current = self
        result = MockCurvePoint(None, None, self.a, self.b)
        n = scalar_int
        while n > 0:
            if n & 1: result = result + current
            current = current + current
            n >>= 1
        return result
    def __eq__(self, other): return (isinstance(other, MockCurvePoint) and self.x == other.x and self.y == other.y and self.a == other.a and self.b == other.b)
    def __hash__(self): return hash((self.x, self.y, self.a, self.b))
    def __repr__(self):
        if self.x is None: return "Point(infinity)"
        return f"Point(x={self.x.num}, y={self.y.num} on E(a={self.a.num},b={self.b.num},p={self.x.prime}))"


def solve_ecdlp_bruteforce(G_point, P_target_point, order_n, max_k_candidate=None):
    """
    Próbuje rozwiązać kG = P metodą siłową.
    G_point: Punkt bazowy.
    P_target_point: Punkt docelowy (klucz publiczny).
    order_n: Rząd grupy (lub podgrupy generowanej przez G).
    max_k_candidate: Opcjonalny limit dla k.
    Zwraca k lub None.
    UWAGA: BARDZO NIEWYDAJNE, tylko dla celów demonstracyjnych na ekstremalnie małych grupach!
    """
    if G_point.x is None:
        print("Punkt bazowy G nie może być punktem w nieskończoności.")
        return None
    
    limit_k = max_k_candidate if max_k_candidate is not None else order_n -1
    print(f"Próba rozwiązania ECDLP: k * {G_point} = {P_target_point}")
    print(f"Metodą siłową (limit k: {limit_k}, rząd grupy n: {order_n})...")
    
    start_time_ecdlp = time.time()
    
    # current_kg = G_point # Zaczynamy od 1*G
    # Możemy zacząć od 0*G = O i dodawać G
    current_kg = MockCurvePoint(None, None, G_point.a, G_point.b) # O (0*G)

    for k_candidate in range(1, limit_k + 1): # Sprawdzamy k od 1 do order_n-1 (lub limit_k)
        # Oblicz k_candidate * G
        # W tej implementacji brute-force, prościej jest dodawać G w każdej iteracji
        current_kg = current_kg + G_point # (k-1)G + G = kG
        
        if current_kg == P_target_point:
            end_time_ecdlp = time.time()
            duration_ecdlp = end_time_ecdlp - start_time_ecdlp
            print(f"Znaleziono skalar k = {k_candidate} w {duration_ecdlp:.4f} sekund.")
            return k_candidate
        
        if k_candidate % (limit_k // 100 if limit_k > 100 else 10) == 0 and limit_k > 1000:
             progress = (k_candidate / limit_k) * 100
             elapsed_time = time.time() - start_time_ecdlp
             print(f"\rPostęp ECDLP Brute-Force: {progress:.2f}% ({k_candidate}/{limit_k}), czas: {elapsed_time:.2f}s", end="")

    end_time_ecdlp = time.time()
    duration_ecdlp = end_time_ecdlp - start_time_ecdlp
    print(f"\nNie znaleziono skalara k w zakresie do {limit_k} (czas: {duration_ecdlp:.4f}s).")
    return None


def run_ecdlp_bruteforce_example():
    print("--- Koncepcyjna Ilustracja 'Brute Force' dla ECDLP ---")

    # Użyjemy tej samej małej krzywej co poprzednio: y^2 = x^3 + 2x + 2 (mod 17)
    # Rząd tej grupy to N = 18.
    p_val = 751 #17
    a_val = -1 #2
    b_val = 1 # 2
    a_fe = MockFiniteFieldElement(a_val, p_val)
    b_fe = MockFiniteFieldElement(b_val, p_val)
    group_order_N = 727 #18 # Rząd pełnej grupy E(F_17)

    # Generator G = (5, 1)
    G = MockCurvePoint(MockFiniteFieldElement(5, p_val), MockFiniteFieldElement(1, p_val), a_fe, b_fe)
    print(f"Punkt bazowy G = {G}")
    print(f"Rząd grupy/podgrupy n = {group_order_N}") # Zakładamy, że G generuje całą grupę

    # Wybierzmy "tajny" skalar (klucz prywatny)
    # Musi być < rzędu grupy. Dla N=18, k może być np. od 1 do 17.
    # Wybierzmy mały skalar, aby brute-force był szybki.
    private_scalar_k = 371 # np.
    print(f"Tajny skalar (klucz prywatny) k = {private_scalar_k}")

    # 1. Łatwa operacja: Mnożenie punktu przez skalar (P = kG)
    print("\nOperacja mnożenia punktu przez skalar (łatwa):")
    start_time_mul = time.time()
    Public_Point_P = private_scalar_k * G
    end_time_mul = time.time()
    duration_mul = end_time_mul - start_time_mul
    print(f"  Punkt publiczny P = {private_scalar_k} * G = {Public_Point_P}")
    print(f"  Czas obliczenia P: {duration_mul:.6f} sekund.  <-- Względnie szybko (choć wolniej niż modular_pow)")

    # 2. "Trudna" operacja: ECDLP (metoda siłowa)
    #    Dla tak małej grupy, brute-force będzie szybki, ale chcemy pokazać ideę.
    #    Limit dla k_candidate ustawiamy na order_n - 1, bo k jest z [1, n-1].
    print(f"\nOperacja ECDLP (metoda siłowa dla małej grupy):")
    
    found_k = solve_ecdlp_bruteforce(G, Public_Point_P, group_order_N, max_k_candidate=group_order_N -1)

    if found_k is not None:
        if found_k == private_scalar_k:
            print(f"\nSukces! Metoda siłowa znalazła poprawny skalar k = {found_k}.")
        else:
            print(f"\nMetoda siłowa znalazła skalar k = {found_k}, który daje ten sam punkt P.")
            print(f"Oryginalny skalar k był {private_scalar_k}.")
            # Tu można by dodać asercję, czy k*G == P
    else:
        print(f"\nMetoda siłowa nie znalazła skalara k.")

    print("\nPodsumowanie:")
    print(f" - Czas mnożenia kG (dla k={private_scalar_k}): {duration_mul:.6f} s")
    # Czas ECDLP brute-force będzie wydrukowany przez funkcję.
    print(" - Czas ECDLP siłowego dla tej małej grupy również jest krótki.")
    print(" - Jednak każda iteracja w ECDLP brute-force (obliczanie k_cand*G lub dodawanie G)")
    print("   jest znacznie bardziej kosztowna niż iteracja w DLP brute-force (g^x_cand mod p).")
    print(" - Dla krzywych o rozmiarach kryptograficznych (np. 256-bitowy rząd n),")
    print("   ECDLP siłowe jest absolutnie niemożliwe (2^256 operacji).")
    print("-----------------------------------------------------------------------\n")



if __name__ == '__main__':
    # run_dlp_example()
    print("\n======================================================================\n")
    run_ecdlp_illustration()
    print("\n======================================================================\n")
    run_ecdlp_bruteforce_example()