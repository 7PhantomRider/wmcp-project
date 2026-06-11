import numpy as np
import random

# false - oryginalne dane z zadania
# true - duża mapa generowana losowo (do testowania skalowalności)
TRYB_LOSOWY = True

if not TRYB_LOSOWY:
    lokalizacje = np.array([[10, 20], [50, 50], [80, 30], [30, 70], [60, 80]])
    cele = np.array([[15, 25], [55, 45], [75, 35], [35, 65], [62, 78], [20, 60], [45, 20]])
    wagi = [1, 10, 5, 3, 8, 2, 4]
    typy_radarow = {"A": 15, "B": 30}
    koszt_radarow = {"A": 100, "B": 200}
    B = 500
else:
    np.random.seed(42)  #seed
    random.seed(42)
    
    liczba_lokalizacji = 70
    liczba_celow = 50
    rozmiar_mapy = 1000
    
    lokalizacje = np.random.uniform(0, rozmiar_mapy, (liczba_lokalizacji, 2))
    cele = np.random.uniform(0, rozmiar_mapy, (liczba_celow, 2))
    wagi = [random.randint(1, 10) for _ in range(liczba_celow)]
    
    typy_radarow = {"A": 50, "B": 120, "C": 250}
    koszt_radarow = {"A": 100, "B": 280, "C": 750}
    B = 3500


I = len(lokalizacje)
J = len(cele)
K = list(typy_radarow.keys())

a = {} # Gurobi i BFO
mapa_pokrycia = {}  # GA

for i in range(I):
    for k in K:
        mapa_pokrycia[(i, k)] = set()
        
for i in range(I):
    for j in range(J):
        for k in K:
            dist = np.linalg.norm(lokalizacje[i] - cele[j])
            zasieg = typy_radarow[k]
            
            if dist <= zasieg:
                a[(i, j, k)] = 1
                mapa_pokrycia[(i, k)].add(j)
            else:
                a[(i, j, k)] = 0

mapa_pokrycia = {}
for i in range(I):
    for k in K:
        mapa_pokrycia[(i, k)] = [j for j in range(J) if a[(i, j, k)] == 1]