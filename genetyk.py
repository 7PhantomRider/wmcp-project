import random
import time
from dane import lokalizacje, cele, wagi, typy_radarow, koszt_radarow, B, I, J, K, mapa_pokrycia


def genetyk():
    start_time = time.time()

    mozliwe_geny = [None] + K

    # Tworzy losowego osobnika
    def losowanie_geny():
        # 90% szans na brak radaru na starcie - ułatwia znalezienie legalnego budżetu!
        return [random.choice(K) if random.random() < 0.1 else None for _ in range(I)]
    
    # Ocenia rozwiazanie
    def ocena_genów(osobnik):
        calkowity_koszt = 0
        zdobyte_cele = set()
        for i, typ_radaru in enumerate(osobnik):
            if typ_radaru is not None:
                calkowity_koszt += koszt_radarow[typ_radaru]
                zdobyte_cele.update(mapa_pokrycia[(i, typ_radaru)])
        
        # Obliczamy zysk z celów
        zysk = sum(wagi[j] for j in zdobyte_cele)
        # Łagodna kara (zamiast kary śmierci) za przekroczenie budżetu
        kara = max(0, calkowity_koszt - B) * 5 
        
        return zysk - kara, calkowity_koszt

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
    najlepszy_wynik = -float('inf')
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

    end_time = time.time()

    postawione = [(i, k) for i, k in enumerate(najlepsze_rozwiazanie) if k is not None]
    
    # Znalezienie pokrytych celów dla tego chromosomu
    zdobyte_cele = set()
    for i, typ_radaru in postawione:
        zdobyte_cele.update(mapa_pokrycia[(i, typ_radaru)])
        
    return {
        "algorytm": "Algorytm Genetyczny",
        "obj": najlepszy_wynik,
        "czas": end_time - start_time,
        "postawione": postawione,
        "pokryte": list(zdobyte_cele)
    }