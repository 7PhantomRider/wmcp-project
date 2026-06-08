import numpy as np

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
# i: 0 - 4

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


# macierz pokrycia a[i][j][k]
#
# a[i][j][k] = 1  jeśli cel j jest w zasięgu radaru k postawionego w lokalizacji i
# a[i][j][k] = 0  w przeciwnym razie

a = {}

for i in range(I):
    for j in range(J):
        for k in K:
            # odległość od lokalizacji i do celu j
            dx = lokalizacje[i][0] - cele[j][0]
            dy = lokalizacje[i][1] - cele[j][1]
            dist = (dx**2 + dy**2) ** 0.5

            zasieg = typy_radarow[k]

            if dist <= zasieg:
                a[(i, j, k)] = 1
            else:
                a[(i, j, k)] = 0

# (ile par (lok, cel) jest w zasięgu każdego typu radaru)
print("liczba par w zasięgu:")
for k in K:
    pokryte = sum(a[(i,j,k)] for i in range(I) for j in range(J))
    print(f"  Typ {k} (zasięg {typy_radarow[k]}): {pokryte} par (lok, cel)")
print()

import numpy as np

# Parametry algorytmu BBFO
liczba_bakterii = 20
liczba_krokow_chemotaksji = 10
dlugosc_plywania = 4
liczba_krokow_reprodukcji = 4
liczba_krokow_eliminacji = 2
prawdopodobienstwo_rozproszenia = 0.25
rozmiar_kroku = 1.0

wymiar = I * len(K)  # 5 lokalizacji * 2 typy = 10 zmiennych

def funkcja_sigmoidalna(wektor):
    wektor = np.clip(wektor, -10, 10) # Zabezpieczenie przed przepełnieniem
    return 1.0 / (1.0 + np.exp(-wektor))

def ocen_bakterie(pozycja_binarna):
    koszt_calkowity = 0
    kara = 0
    pokryte_cele = set()
    
    # Dekodowanie 10-bitowego wektora na konkretne lokalizacje i typy
    for idx_k, k in enumerate(K):
        for i in range(I):
            indeks_bitu = idx_k * I + i
            if pozycja_binarna[indeks_bitu] == 1:
                koszt_calkowity += koszt_radarow[k]
                
                # Zbieranie pokrytych celów dla tego radaru
                for j in range(J):
                    if a[(i, j, k)] == 1:
                        pokryte_cele.add(j)
                        
    # Ograniczenie 1: Budżet
    if koszt_calkowity > B:
        kara += (koszt_calkowity - B) * 1000
        
    # Ograniczenie 2: Maksymalnie jeden radar na lokalizację
    for i in range(I):
        liczba_radarow_w_lokalizacji = pozycja_binarna[0 * I + i] + pozycja_binarna[1 * I + i]
        if liczba_radarow_w_lokalizacji > 1:
            kara += 2000
            
    zysk = sum(wagi[j] for j in pokryte_cele)
    
    # Minimalizujemy, więc zwracamy ujemny zysk + kary
    return -zysk + kara

# Inicjalizacja populacji
bakterie_ciagle = np.random.uniform(-2, 2, (liczba_bakterii, wymiar))
bakterie_binarne = np.zeros((liczba_bakterii, wymiar), dtype=int)
zdrowie_bakterii = np.zeros(liczba_bakterii)

for b in range(liczba_bakterii):
    prawdopodobienstwo = funkcja_sigmoidalna(bakterie_ciagle[b])
    bakterie_binarne[b] = (np.random.rand(wymiar) < prawdopodobienstwo).astype(int)
    zdrowie_bakterii[b] = ocen_bakterie(bakterie_binarne[b])

najlepsza_pozycja_globalnie = None
najlepszy_koszt_globalnie = float('inf')

# Główna pętla BBFO
for l in range(liczba_krokow_eliminacji):
    for k_rep in range(liczba_krokow_reprodukcji):
        for j_chem in range(liczba_krokow_chemotaksji):
            
            for b in range(liczba_bakterii):
                # Koziołkowanie (Tumble)
                delta = np.random.uniform(-1, 1, wymiar)
                norma = np.linalg.norm(delta)
                kierunek = delta / norma if norma > 0 else np.zeros(wymiar)
                
                nowa_pozycja_ciagla = bakterie_ciagle[b] + rozmiar_kroku * kierunek
                
                # Transformacja na binarne
                prawdopodobienstwo = funkcja_sigmoidalna(nowa_pozycja_ciagla)
                nowa_pozycja_binarna = (np.random.rand(wymiar) < prawdopodobienstwo).astype(int)
                nowy_koszt = ocen_bakterie(nowa_pozycja_binarna)
                
                # Pływanie (Swim)
                m = 0
                while m < dlugosc_plywania:
                    if nowy_koszt < zdrowie_bakterii[b]:
                        bakterie_ciagle[b] = nowa_pozycja_ciagla
                        bakterie_binarne[b] = nowa_pozycja_binarna
                        zdrowie_bakterii[b] = nowy_koszt
                        
                        if nowy_koszt < najlepszy_koszt_globalnie:
                            najlepszy_koszt_globalnie = nowy_koszt
                            najlepsza_pozycja_globalnie = nowa_pozycja_binarna.copy()
                            
                        # Kolejny krok w tym samym kierunku
                        nowa_pozycja_ciagla = bakterie_ciagle[b] + rozmiar_kroku * kierunek
                        prawdopodobienstwo = funkcja_sigmoidalna(nowa_pozycja_ciagla)
                        nowa_pozycja_binarna = (np.random.rand(wymiar) < prawdopodobienstwo).astype(int)
                        nowy_koszt = ocen_bakterie(nowa_pozycja_binarna)
                        m += 1
                    else:
                        m = dlugosc_plywania
                        
        # Reprodukcja
        indeksy_sortowania = np.argsort(zdrowie_bakterii)
        bakterie_ciagle = bakterie_ciagle[indeksy_sortowania]
        bakterie_binarne = bakterie_binarne[indeksy_sortowania]
        zdrowie_bakterii = zdrowie_bakterii[indeksy_sortowania]
        
        polowa = liczba_bakterii // 2
        for b in range(polowa):
            bakterie_ciagle[b + polowa] = bakterie_ciagle[b].copy()
            bakterie_binarne[b + polowa] = bakterie_binarne[b].copy()
            zdrowie_bakterii[b + polowa] = zdrowie_bakterii[b]
            
    # Eliminacja i rozpraszanie
    for b in range(liczba_bakterii):
        if np.random.rand() < prawdopodobienstwo_rozproszenia:
            bakterie_ciagle[b] = np.random.uniform(-2, 2, wymiar)
            prawdopodobienstwo = funkcja_sigmoidalna(bakterie_ciagle[b])
            bakterie_binarne[b] = (np.random.rand(wymiar) < prawdopodobienstwo).astype(int)
            zdrowie_bakterii[b] = ocen_bakterie(bakterie_binarne[b])
            
            if zdrowie_bakterii[b] < najlepszy_koszt_globalnie:
                najlepszy_koszt_globalnie = zdrowie_bakterii[b]
                najlepsza_pozycja_globalnie = bakterie_binarne[b].copy()

print("Maksymalny uzyskany zysk:", -najlepszy_koszt_globalnie)
print("Konfiguracja radarów:")

calkowity_koszt_rozwiazania = 0
for idx_k, k in enumerate(K):
    for i in range(I):
        indeks_bitu = idx_k * I + i
        if najlepsza_pozycja_globalnie[indeks_bitu] == 1:
            print(f"- Lokalizacja {i} {lokalizacje[i]}, Typ: {k} (Koszt: {koszt_radarow[k]})")
            calkowity_koszt_rozwiazania += koszt_radarow[k]
            
print(f"Wykorzystany budżet: {calkowity_koszt_rozwiazania} / {B}")