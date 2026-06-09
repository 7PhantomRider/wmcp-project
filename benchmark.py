from solver import solver
from genetyk import genetyk
from DBFO import DBFO
from visualize import rysuj_mape

print("==================================================")
print(" ROZPOCZYNAM TESTOWANIE ALGORYTMÓW (WMCP)")
print("==================================================\n")

# 1. GUROBI
print("[1/3] Uruchamianie Gurobi (Optimum)...")
wyniki_gurobi = solver()
rysuj_mape(wyniki_gurobi, "mapa_gurobi.png")

# 2. GENETYK
print("[2/3] Uruchamianie Algorytmu Genetycznego...")
wyniki_ga = genetyk()
rysuj_mape(wyniki_ga, "mapa_ga.png")

# 3. DBFO
print("[3/3] Uruchamianie DBFO (Bakterie)...")
wyniki_dbfo = DBFO()
rysuj_mape(wyniki_dbfo, "mapa_dbfo.png")

print("\n==================================================")
print(" WYNIKI KOŃCOWE")
print("==================================================")
print(f"{'Algorytm':<25} | {'Zysk (Funkcja Celu)':<20} | {'Czas [s]':<10}")
print("-" * 60)
print(f"{wyniki_gurobi['algorytm']:<25} | {wyniki_gurobi['obj']:<20.1f} | {wyniki_gurobi['czas']:.4f}")
print(f"{wyniki_ga['algorytm']:<25} | {wyniki_ga['obj']:<20.1f} | {wyniki_ga['czas']:.4f}")
print(f"{wyniki_dbfo['algorytm']:<25} | {wyniki_dbfo['obj']:<20.1f} | {wyniki_dbfo['czas']:.4f}")
print("==================================================\n")
print("Wygenerowano pliki: mapa_gurobi.png, mapa_ga.png, mapa_dbfo.png")