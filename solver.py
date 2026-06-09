import gurobipy as gp
from gurobipy import GRB
import time

from dane import lokalizacje, cele, wagi, typy_radarow, koszt_radarow, B, I, J, K, a


def solver():

    start_time = time.time()

    # MODEL

    model = gp.Model("WMCP")

    # (opcjonalny filtr outputu tu gdzieś znalazłem zeby czystszy tekst był)
    model.setParam("OutputFlag", 0)


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

    # budzet: suma kosztow radarow nie moze przekroczyc B
    model.addConstr(
        gp.quicksum(koszt_radarow[k] * x[i, k] for i in range(I) for k in K) <= B,
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
    end_time = time.time()

    # WYNIKI

    postawione = [(i, k) for i in range(I) for k in K if x[i, k].X > 0.5]
    pokryte = [j for j in range(J) if y[j].X > 0.5]
    obj_val = model.ObjVal if model.Status == GRB.OPTIMAL else None

    return {
        "algorytm": "ILP (Gurobi)",
        "postawione": postawione,
        "pokryte": pokryte,
        "obj": obj_val,
        "czas": end_time - start_time
    }