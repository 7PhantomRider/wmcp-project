#!pip install gurobipy

import gurobipy as gp
from gurobipy import GRB
import numpy as np

# WMCP — Weighted Maximum Coverage Problem
# Rozmieszczamy radary, żeby pokryć jak najważniejsze cele


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

# budzet ilościowy radarów
N = 3

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


# MODEL

model = gp.Model("WMCP")

# (opcjonalny filtr outputu tu gdzieś znalazłem zeby czystszy tekst był)
# model.setParam("OutputFlag", 0)


# ZMIENNE DECYZYJNE

# x[i, k] = 1  jeśli w lokalizacji i postawiono radar typu k
#          = 0  w przeciwnym razie
x = model.addVars(I, K, vtype=GRB.BINARY, name="x")

# y[j] = 1  jeśli cel j jest pokryty przez co najmniej jeden radar
#       = 0  w przeciwnym razie
y = model.addVars(J, vtype=GRB.BINARY, name="y")


# FUNKCJA CELU
# maksymalizacja sumy wag pokrytych celów

model.setObjective(
    gp.quicksum(wagi[j] * y[j] for j in range(J)),
    GRB.MAXIMIZE
)


# OGRANICZENIA

# budzet max N radarów
model.addConstr(
    gp.quicksum(x[i, k] for i in range(I) for k in K) <= N,
    name="budzet"
)

# y[j] moze być 1 tylko jeśli jest pokryty przez co najmniej jeden radar
for j in range(J):
    model.addConstr(
        y[j] <= gp.quicksum(a[(i, j, k)] * x[i, k] for i in range(I) for k in K),
        name=f"pokrycie_celu_{j}"
    )

# jeden radar na lokalizację (nie można postawić dwóch radarów w tym samym miejscu)
for i in range(I):
    model.addConstr(
        gp.quicksum(x[i, k] for k in K) <= 1,
        name=f"jeden_radar_lok_{i}"
    )


# OPTIMIZE RUN

model.optimize()


# WYNIKI


print("\n\nWYNIKI")


if model.Status == GRB.OPTIMAL:
    print(f"status: OPTIMAL")
    print(f"funkcja celu: {model.ObjVal:.1f}  (max możliwe: {sum(wagi)})")
    print()

    print("rozmieszczenie radarów:")
    for i in range(I):
        for k in K:
            if x[i, k].X > 0.5:   # > 0.5 bo zmienna binarna (float zaokrąglony)
                print(f"  lokalizacja {i} {lokalizacje[i]} -> radar typ {k} (zasięg {typy_radarow[k]})")

    print()
    print("pokryte cele:")
    for j in range(J):
        if y[j].X > 0.5:
            print(f"  cel {j} {cele[j]}  waga={wagi[j]}")

    print()
    print("niepokryte cele:")
    for j in range(J):
        if y[j].X < 0.5:
            print(f"  cel {j} {cele[j]}  waga={wagi[j]}")

else:
    print(f"status: {model.Status} — brak rozwiązania")