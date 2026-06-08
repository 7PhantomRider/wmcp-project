import numpy as np
import random

# DANE

# obszar: kwadrat 100 x 100 jednostek
# każdy punkt to (x, y)

# gdzie możemy postawić radary
lokalizacje = np.array([
    [10, 20],
    [50, 50],
    [80, 30],
    [30, 70],
    [60, 80],
])
# i: 0, 1, 2, 3, 4

# pokrywane cele. i od 0 do 6 (7 celów)
cele = np.array([
    [15, 25],
    [55, 45],
    [75, 35],
    [35, 65],
    [62, 78],
    [20, 60],
    [45, 20],
])

# weight
wagi = [1, 10, 5, 3, 8, 2, 4]

# typy radarów i ich zasięgi
typy_radarow = {
    "A": 15,
    "B": 30,
}

# koszt każdego typu radaru
koszt_radarow = {
    "A": 100,
    "B": 200
}
# budzet 
B = 500

# zmienne dot rozmiarów
I = len(lokalizacje)    # liczba lokalizacji
J = len(cele)           # liczba celów
K = list(typy_radarow.keys())   # ['A', 'B']


# zamiast macierzy pokrycia a[i][j][k] - mapa pokrycia 
mapa_pokrycia = {}
for i in range(I):
    for k in K:
        pokryte_cele = set()
        for j in range(J):
            # Odleglosc od lokalizacji i do celu j
            dx = lokalizacje[i][0] - cele[j][0]
            dy = lokalizacje[i][1] - cele[j][1]
            dystans = (dx**2 + dy**2) ** 0.5
            zasieg = typy_radarow[k]
            if dystans <= zasieg:
                pokryte_cele.add(j)
        mapa_pokrycia[(i, k)] = pokryte_cele


mozliwe_geny = [None] + K

# Tworzy losowego osobnika
def losowanie_geny():
    return [random.choice(mozliwe_geny) for _ in range(I)]

# Ocenia rozwiazanie
def ocena_genów(osobnik):
    calkowity_koszt = 0
    zdobyte_cele = set()
    
    for i, typ_radaru in enumerate(osobnik):
        if typ_radaru is not None:
            calkowity_koszt += koszt_radarow[typ_radaru]
            zdobyte_cele.update(mapa_pokrycia[(i, typ_radaru)])
            
    # Ograniczenie budzetowe
    if calkowity_koszt > B:
        return 0, calkowity_koszt 
        
    # Sumowanie wag pokrytych celow
    calkowita_waga = sum(wagi[j] for j in zdobyte_cele)
    return calkowita_waga, calkowity_koszt

# Krzyzowanie dwoch rodzicow
def krzyzowanie(rodzic1, rodzic2):
    punkt_podzialu = random.randint(1, len(rodzic1) - 1)
    dziecko1 = rodzic1[:punkt_podzialu] + rodzic2[punkt_podzialu:]
    dziecko2 = rodzic2[:punkt_podzialu] + rodzic1[punkt_podzialu:]
    return dziecko1, dziecko2

# Mutacja z okreslonym prawdopodobienstwem
def mutacja(osobnik, szansa_mutacji=0.1):
    for i in range(len(osobnik)):
        if random.random() < szansa_mutacji:
            osobnik[i] = random.choice(mozliwe_geny)
    return osobnik

# Wybor rodzica
def selekcja_turniejowa(populacja, oceny, rozmiar_turnieju=3):
    wybrane_indeksy = random.sample(range(len(populacja)), rozmiar_turnieju)
    najlepszy_indeks = max(wybrane_indeksy, key=lambda idx: oceny[idx][0])
    return populacja[najlepszy_indeks]


ROZMIAR_POPULACJI = 100
LICZBA_POKOLEN = 150
SZANSA_MUTACJI = 0.15

# Startowa populacja
populacja = [losowanie_geny() for _ in range(ROZMIAR_POPULACJI)]

najlepsze_rozwiazanie = None
najlepszy_wynik = -1
najlepszy_koszt = 0

for pokolenie in range(LICZBA_POKOLEN):
    oceny = [ocena_genów(osobnik) for osobnik in populacja]
    
    # Znalezienie najlepszego osobnika
    for osobnik, ocena in zip(populacja, oceny):
        if ocena[0] > najlepszy_wynik or (ocena[0] == najlepszy_wynik and ocena[1] < najlepszy_koszt):
            najlepszy_wynik = ocena[0]
            najlepszy_koszt = ocena[1]
            najlepsze_rozwiazanie = list(osobnik)
            
    # Nowe pokolenie zaczyna z najlepszym rozwiazaniem z poprzedniego
    nowa_populacja = [najlepsze_rozwiazanie]
    
    # Wypelnianie populacji nowymi osobnikami
    while len(nowa_populacja) < ROZMIAR_POPULACJI:
        rodzic1 = selekcja_turniejowa(populacja, oceny)
        rodzic2 = selekcja_turniejowa(populacja, oceny)
        
        dziecko1, dziecko2 = krzyzowanie(rodzic1, rodzic2)
        
        dziecko1 = mutacja(dziecko1, SZANSA_MUTACJI)
        dziecko2 = mutacja(dziecko2, SZANSA_MUTACJI)
        
        nowa_populacja.extend([dziecko1, dziecko2])
        
    populacja = nowa_populacja[:ROZMIAR_POPULACJI]

# Wypisanie wyniku
print("\nNajlepsze rozwiazanie:")
print(f"Zdobyta suma wag: {najlepszy_wynik}")
print(f"Wykorzystany budzet: {najlepszy_koszt} / {B}")
for i, typ_radaru in enumerate(najlepsze_rozwiazanie):
    if typ_radaru is not None:
        print(f"  - Lokalizacja {i} ({lokalizacje[i][0]}, {lokalizacje[i][1]}): Radar {typ_radaru}")
