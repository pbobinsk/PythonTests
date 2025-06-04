# --- Przykład: Problem Logarytmu Dyskretnego (DLP) w F_p* ---

def modular_pow(base, exponent, modulus):
    """Oblicza (base^exponent) % modulus efektywnie."""
    return pow(base, exponent, modulus)

import time

def solve_dlp_bruteforce(g, h, p):
    """
    Próbuje rozwiązać g^x = h (mod p) metodą siłową.
    Zwraca x lub None, jeśli nie znaleziono w rozsądnym zakresie (tutaj do p-1).
    UWAGA: Tylko dla celów demonstracyjnych i małych p!
    """
    if not (1 <= g < p and 1 <= h < p):
        print("g i h muszą być w zakresie [1, p-1]")
        return None
    
    print(f"Próba rozwiązania DLP: {g}^x = {h} (mod {p})")
    for x_candidate in range(1, p): # x może być z zakresu [1, p-1] (lub nawet [0, p-2] jeśli rząd jest p-1)
        if modular_pow(g, x_candidate, p) == h:
            print(f"Znaleziono x = {x_candidate}")
            return x_candidate
    print(f"Nie znaleziono x dla g={g}, h={h}, p={p} w zakresie do {p-1}")
    return None


def run_dlp_example():
    print("--- Przykład: Problem Logarytmu Dyskretnego (DLP) w F_p* ---")

    # Parametry dla małej grupy
    p_small = 23
    g_small = 5  # Generator dla F_23*

    # 1. Łatwa operacja: Potęgowanie modularne
    x_known = 9
    h_calculated = modular_pow(g_small, x_known, p_small)
    print(f"Potęgowanie: {g_small}^{x_known} (mod {p_small}) = {h_calculated}  <-- TO JEST ŁATWE")

    # 2. Trudna operacja (dla dużych p): Logarytm dyskretny
    #    Spróbujmy znaleźć x dla h_calculated
    print("\nLogarytmowanie (dla małego p, metoda siłowa):")
    t1 = time.time()
    found_x = solve_dlp_bruteforce(g_small, h_calculated, p_small)
    t2 = time.time()
    if found_x is not None:
        assert found_x == x_known or modular_pow(g_small, found_x, p_small) == modular_pow(g_small, x_known, p_small)
        # Uwaga: może istnieć wiele x, jeśli rząd g jest mniejszy niż p-1. Tutaj x_known jest jednym z nich.

    print("\n--- Inny przykład dla DLP ---")
    p_medium = 16777213 # Trochę większa liczba pierwsza
    g_medium = 7    # Przyjmijmy, że to generator (lub element o dużym rzędzie)
    x_secret = 776534
    h_target = modular_pow(g_medium, x_secret, p_medium)
    print(f"Dla p={p_medium}, g={g_medium}, niech h = g^x = {h_target}")
    print("Znalezienie x takiego, że 7^x =",h_target,f"(mod {p_medium}) jest już bardziej czasochłonne siłowo.")
    # Nie będziemy tu uruchamiać solve_dlp_bruteforce dla p_medium, bo zajęłoby to chwilę.
    # Dla p ~2048 bitów, metoda siłowa jest niemożliwa.
    print("\nLogarytmowanie (dla średniego p, metoda siłowa):")
    t3 = time.time()
    found_x = solve_dlp_bruteforce(g_medium, h_target, p_medium)
    t4 = time.time()
    if found_x is not None:
        assert found_x == x_secret or modular_pow(g_medium, found_x, p_medium) == modular_pow(g_medium, x_secret, p_medium)
        # Uwaga: może istnieć wiele x, jeśli rząd g jest mniejszy niż p-1. Tutaj x_known jest jednym z nich.


    print(f"{t2-t1:.2f} s, {t4-t3:.2f} s")
    print("\nDyskusja:")
    print(" - Potęgowanie modularne jest szybkie dzięki algorytmom takim jak 'potęgowanie przez podnoszenie do kwadratu'.")
    print(" - Odwrotna operacja, logarytm dyskretny, jest trudna dla dużych liczb pierwszych p.")
    print(" - Bezpieczeństwo kryptosystemów takich jak Diffie-Hellman czy ElGamal opiera się na tej trudności.")
    print("-------------------------------------------------------------\n")

if __name__ == '__main__':
    run_dlp_example()