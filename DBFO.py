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

# wagi
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
a = {}

for i in range(I):
    for j in range(J):
        for k in K:
            dx = lokalizacje[i][0] - cele[j][0]
            dy = lokalizacje[i][1] - cele[j][1]
            dist = (dx**2 + dy**2) ** 0.5

            zasieg = typy_radarow[k]

            if dist <= zasieg:
                a[(i, j, k)] = 1
            else:
                a[(i, j, k)] = 0

print("Liczba par w zasięgu:")
for k in K:
    pokryte = sum(a[(i,j,k)] for i in range(I) for j in range(J))
    print(f"  Typ {k} (zasięg {typy_radarow[k]}): {pokryte} par (lok, cel)")
print()

# ALGORYTM DBFO (Dyskretne BFO)

liczba_bakterii = 20
liczba_krokow_chemotaksji = 10
dlugosc_plywania = 4
liczba_krokow_reprodukcji = 4
liczba_krokow_eliminacji = 2
prawdopodobienstwo_rozproszenia = 0.25
rozmiar_kroku = 1.0

wymiar = I  

def funkcja_sigmoidalna(wektor):
    wektor_obciety = np.clip(wektor, -10, 10)
    return 1.0 / (1.0 + np.exp(-wektor_obciety))

def dekoduj_na_stany(wektor_ciagly):
    prawdopodobienstwa = funkcja_sigmoidalna(wektor_ciagly)
    stany = np.zeros(wymiar, dtype=int)
    
    stany[prawdopodobienstwa >= 0.33] = 1  
    stany[prawdopodobienstwa >= 0.66] = 2  
    return stany

def ocen_bakterie(stany_lokalizacji):
    koszt_calkowity = 0
    pokryte_cele = set()
    
    for i in range(wymiar):
        stan = stany_lokalizacji[i]
        if stan == 0:
            continue
            
        k = K[stan - 1] 
        koszt_calkowity += koszt_radarow[k]
        
        for j in range(J):
            if a[(i, j, k)] == 1:
                pokryte_cele.add(j)
                
    kara = 0
    if koszt_calkowity > B:
        kara += (koszt_calkowity - B) * 1000
        
    zysk = sum(wagi[j] for j in pokryte_cele)
    return -zysk + kara


bakterie_ciagle = np.random.uniform(-2, 2, (liczba_bakterii, wymiar))
bakterie_dyskretne = np.zeros((liczba_bakterii, wymiar), dtype=int)
zdrowie_bakterii = np.zeros(liczba_bakterii)

for b in range(liczba_bakterii):
    bakterie_dyskretne[b] = dekoduj_na_stany(bakterie_ciagle[b])
    zdrowie_bakterii[b] = ocen_bakterie(bakterie_dyskretne[b])

najlepsza_pozycja_globalnie = None
najlepszy_koszt_globalnie = float('inf')


for l in range(liczba_krokow_eliminacji):
    for k_rep in range(liczba_krokow_reprodukcji):
        for j_chem in range(liczba_krokow_chemotaksji):
            
            for b in range(liczba_bakterii):
                delta = np.random.uniform(-1, 1, wymiar)
                norma = np.linalg.norm(delta)
                kierunek = delta / norma if norma > 0 else np.zeros(wymiar)
                
                nowa_pozycja_ciagla = bakterie_ciagle[b] + rozmiar_kroku * kierunek
                nowa_pozycja_dyskretna = dekoduj_na_stany(nowa_pozycja_ciagla)
                nowy_koszt = ocen_bakterie(nowa_pozycja_dyskretna)
                
                m = 0
                while m < dlugosc_plywania:
                    if nowy_koszt < zdrowie_bakterii[b]:
                        bakterie_ciagle[b] = nowa_pozycja_ciagla
                        bakterie_dyskretne[b] = nowa_pozycja_dyskretna
                        zdrowie_bakterii[b] = nowy_koszt
                        
                        if nowy_koszt < najlepszy_koszt_globalnie:
                            najlepszy_koszt_globalnie = nowy_koszt
                            najlepsza_pozycja_globalnie = nowa_pozycja_dyskretna.copy()
                            
                        nowa_pozycja_ciagla = bakterie_ciagle[b] + rozmiar_kroku * kierunek
                        nowa_pozycja_dyskretna = dekoduj_na_stany(nowa_pozycja_ciagla)
                        nowy_koszt = ocen_bakterie(nowa_pozycja_dyskretna)
                        m += 1
                    else:
                        m = dlugosc_plywania
                        
        indeksy_sortowania = np.argsort(zdrowie_bakterii)
        bakterie_ciagle = bakterie_ciagle[indeksy_sortowania]
        bakterie_dyskretne = bakterie_dyskretne[indeksy_sortowania]
        zdrowie_bakterii = zdrowie_bakterii[indeksy_sortowania]
        
        polowa = liczba_bakterii // 2
        for b in range(polowa):
            bakterie_ciagle[b + polowa] = bakterie_ciagle[b].copy()
            bakterie_dyskretne[b + polowa] = bakterie_dyskretne[b].copy()
            zdrowie_bakterii[b + polowa] = zdrowie_bakterii[b]
            
    for b in range(liczba_bakterii):
        if np.random.rand() < prawdopodobienstwo_rozproszenia:
            bakterie_ciagle[b] = np.random.uniform(-2, 2, wymiar)
            bakterie_dyskretne[b] = dekoduj_na_stany(bakterie_ciagle[b])
            zdrowie_bakterii[b] = ocen_bakterie(bakterie_dyskretne[b])
            
            if zdrowie_bakterii[b] < najlepszy_koszt_globalnie:
                najlepszy_koszt_globalnie = zdrowie_bakterii[b]
                najlepsza_pozycja_globalnie = bakterie_dyskretne[b].copy()

# WYNIKI
print("Maksymalny uzyskany zysk:", -najlepszy_koszt_globalnie)
print("Rozmieszczenie radarów:")

calkowity_koszt_rozwiazania = 0
for i in range(wymiar):
    stan = najlepsza_pozycja_globalnie[i]
    if stan > 0:
        k = K[stan - 1]
        print(f"- Lokalizacja {i} {lokalizacje[i]}, Typ: {k} (Koszt: {koszt_radarow[k]})")
        calkowity_koszt_rozwiazania += koszt_radarow[k]
        
print(f"Wykorzystany budżet: {calkowity_koszt_rozwiazania} / {B}")
