import streamlit as st
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import matplotlib.pyplot as plt

# config
st.set_page_config(layout="wide", page_title="Optymalizacja Radarów")
st.title("wieghted maximum coverage")

# menu
st.sidebar.header("Ustawienia Modelu")

# Suwaki do parametrów
B = st.sidebar.slider("Budżet (B)", min_value=100, max_value=2000, value=500, step=100)

st.sidebar.subheader("Radary typu A")
zasieg_A = st.sidebar.slider("Zasięg A", 5, 50, 15)
koszt_A = st.sidebar.slider("Koszt A", 10, 300, 100, step=10)

st.sidebar.subheader("Radary typu B")
zasieg_B = st.sidebar.slider("Zasięg B", 10, 80, 30)
koszt_B = st.sidebar.slider("Koszt B", 50, 500, 200, step=10)

# Ustawienia obszaru i losowania (żeby móc zmieniać liczbę celów i lokalizacji)
st.sidebar.subheader("Mapa")
liczba_lokalizacji = st.sidebar.slider("Liczba potencjalnych lokalizacji", 3, 20, 5)
liczba_celow = st.sidebar.slider("Liczba celów", 3, 30, 7)

# Używamy st.session_state, żeby pozycje nie skakały przy każdym ruchu suwaka budżetu
if 'wygenerowane' not in st.session_state or st.sidebar.button("Losuj nową mapę"):
    st.session_state.lokalizacje = np.random.randint(5, 95, size=(liczba_lokalizacji, 2))
    st.session_state.cele = np.random.randint(5, 95, size=(liczba_celow, 2))
    st.session_state.wagi = np.random.randint(1, 11, size=liczba_celow)
    st.session_state.wygenerowane = True

lokalizacje = st.session_state.lokalizacje
cele = st.session_state.cele
wagi = st.session_state.wagi

typy_radarow = {"A": zasieg_A, "B": zasieg_B}
koszt_radarow = {"A": koszt_A, "B": koszt_B}

I = len(lokalizacje)
J = len(cele)
K = list(typy_radarow.keys())

# kod
a = {}
for i in range(I):
    for j in range(J):
        for k in K:
            dx = lokalizacje[i][0] - cele[j][0]
            dy = lokalizacje[i][1] - cele[j][1]
            dist = (dx**2 + dy**2) ** 0.5
            a[(i, j, k)] = 1 if dist <= typy_radarow[k] else 0

# Środowisko Gurobi (wyciszamy logi w konsoli, żeby nie śmiecić)
env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("WMCP", env=env)
x = model.addVars(I, K, vtype=GRB.BINARY, name="x")
y = model.addVars(J, vtype=GRB.BINARY, name="y")

model.setObjective(gp.quicksum(wagi[j] * y[j] for j in range(J)), GRB.MAXIMIZE)

model.addConstr(gp.quicksum(koszt_radarow[k] * x[i, k] for i in range(I) for k in K) <= B, name="budzet")
for j in range(J):
    model.addConstr(y[j] <= gp.quicksum(a[(i, j, k)] * x[i, k] for i in range(I) for k in K))
for i in range(I):
    model.addConstr(gp.quicksum(x[i, k] for k in K) <= 1)

model.optimize()

# VIZ 1
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Mapa Rozmieszczenia")
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.grid(True, linestyle='--', alpha=0.5)

    # Rysowanie wszystkich potencjalnych lokalizacji
    ax.scatter(lokalizacje[:, 0], lokalizacje[:, 1], c='gray', marker='s', label='Puste lokalizacje')

    # Rysowanie wyników
    if model.Status == GRB.OPTIMAL:
        # Rysujemy pokryte i niepokryte cele
        for j in range(J):
            if y[j].X > 0.5:
                ax.scatter(cele[j][0], cele[j][1], c='green', marker='*', s=wagi[j]*20)
                ax.text(cele[j][0]+1, cele[j][1]+1, f"{wagi[j]}", color='green')
            else:
                ax.scatter(cele[j][0], cele[j][1], c='red', marker='*', s=wagi[j]*20)
                ax.text(cele[j][0]+1, cele[j][1]+1, f"{wagi[j]}", color='red')

        # postawione radary i ich zasięgi
        colors = {"A": "blue", "B": "purple"}
        for i in range(I):
            for k in K:
                if x[i, k].X > 0.5:
                    # radar
                    ax.scatter(lokalizacje[i][0], lokalizacje[i][1], c=colors[k], marker='s', s=100)
                    ax.text(lokalizacje[i][0]-3, lokalizacje[i][1]+3, f"Typ {k}", fontweight='bold')
                    # range
                    circle = plt.Circle((lokalizacje[i][0], lokalizacje[i][1]), typy_radarow[k], color=colors[k], alpha=0.2)
                    ax.add_patch(circle)
        
        # Legenda własna
        ax.plot([], [], 's', color='blue', label='Zbudowany Radar A')
        ax.plot([], [], 's', color='purple', label='Zbudowany Radar B')
        ax.plot([], [], '*', color='green', label='Cel pokryty')
        ax.plot([], [], '*', color='red', label='Cel niepokryty')
        ax.legend(loc="upper right")
        
        st.pyplot(fig)
    else:
        st.error("Brak rozwiązania optymalnego! Prawdopodobnie budżet jest za mały, by cokolwiek postawić.")

with col2:
    st.subheader("Statystyki Gurobi")
    if model.Status == GRB.OPTIMAL:
        max_mozliwe = sum(wagi)
        zdobyte = model.ObjVal
        st.metric(label="Zabezpieczona wartość strategiczna", value=f"{zdobyte:.0f} / {max_mozliwe}")
        
        koszt_calkowity = sum(koszt_radarow[k] for i in range(I) for k in K if x[i,k].X > 0.5)
        st.metric(label="Wydany budżet", value=f"{koszt_calkowity} / {B}")
        
        st.write("---")
        st.write("**Szczegóły konstrukcji:**")
        for i in range(I):
            for k in K:
                if x[i, k].X > 0.5:
                    st.success(f"Radar {k} w lokalizacji {i}")