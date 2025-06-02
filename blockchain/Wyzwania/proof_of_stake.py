import random

def select_validator_weighted(validators_stakes, num_to_select=1):
    """
    Prosta symulacja wyboru walidatora na podstawie wielkości stake'u.
    validators_stakes: Słownik {'nazwa_walidatora': ilosc_stake'u}
    num_to_select: Ilu walidatorów wylosować (np. dla komitetu)
    """
    if not validators_stakes:
        return []

    population = []
    weights = []
    for validator, stake in validators_stakes.items():
        population.append(validator)
        weights.append(stake) # Waga to po prostu stake

    # random.choices pozwala na losowanie z wagami i z powtórzeniami (jeśli num_to_select > 1)
    # k - liczba elementów do wylosowania
    selected = random.choices(population, weights=weights, k=num_to_select)
    return selected

# Przykład użycia:
stakes = {
    "Walidator_A": 100,  # Ma 100 jednostek stake'u
    "Walidator_B": 50,
    "Walidator_C": 200, # Największy stake, największa szansa
    "Walidator_D": 10,
    "Walidator_E": 75
}

print("Stawki walidatorów:", stakes)

# Symulujmy wybór lidera do stworzenia następnego bloku
next_block_creator = select_validator_weighted(stakes, 1)[0]
print(f"\nWylosowany twórca następnego bloku: {next_block_creator}")

# Symulujmy wybór komitetu walidującego (np. 3 członków)
# committee_size = 3
# validation_committee = select_validator_weighted(stakes, committee_size)
# print(f"\nWylosowany komitet walidujący ({committee_size} członków): {validation_committee}")

# Można uruchomić wielokrotnie, aby zobaczyć, że częściej wybierani są ci z większym stake'iem
print("\nSymulacja wielokrotnego wyboru lidera (np. 1000 razy):")
selections_count = {validator: 0 for validator in stakes.keys()}
for _ in range(1000):
    winner = select_validator_weighted(stakes, 1)[0]
    selections_count[winner] += 1
print(selections_count)