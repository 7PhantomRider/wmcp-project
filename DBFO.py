import numpy as np
import time
from dane import lokalizacje, cele, wagi, typy_radarow, koszt_radarow, B, I, J, K, a

# ALGORYTM DBFO (Dyskretne BFO)

def DBFO():
    start_time = time.time()
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
        
        stany[prawdopodobienstwa >= 0.25] = 1  
        stany[prawdopodobienstwa >= 0.50] = 2  
        stany[prawdopodobienstwa >= 0.75] = 3 
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


    bakterie_ciagle = np.random.uniform(-4, 0, (liczba_bakterii, wymiar))
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
                bakterie_ciagle[b] = np.random.uniform(-4, 0, wymiar)
                bakterie_dyskretne[b] = dekoduj_na_stany(bakterie_ciagle[b])
                zdrowie_bakterii[b] = ocen_bakterie(bakterie_dyskretne[b])
                
                if zdrowie_bakterii[b] < najlepszy_koszt_globalnie:
                    najlepszy_koszt_globalnie = zdrowie_bakterii[b]
                    najlepsza_pozycja_globalnie = bakterie_dyskretne[b].copy()
    end_time = time.time()

    postawione = []
    pokryte = set()
    
    for i in range(wymiar):
        stan = najlepsza_pozycja_globalnie[i]
        if stan > 0:
            k = K[stan - 1]
            postawione.append((i, k))
            for j in range(J):
                if a[(i, j, k)] == 1:
                    pokryte.add(j)

    return {
        "algorytm": "Dyskretne BFO",
        "obj": -najlepszy_koszt_globalnie, # Odwrócenie minusa z fitnessu
        "czas": end_time - start_time,
        "postawione": postawione,
        "pokryte": list(pokryte)
    }