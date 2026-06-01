import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

from solver import wyniki

lokalizacje  = wyniki["lokalizacje"]
cele         = wyniki["cele"]
wagi         = wyniki["wagi"]
typy_radarow = wyniki["typy_radarow"]
postawione   = wyniki["postawione"]   # lista (i, k)
pokryte      = wyniki["pokryte"]      # lista j
obj          = wyniki["obj"]


# map
fig, ax = plt.subplots(figsize=(9, 8))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_aspect("equal")
ax.set_facecolor("#f5f5f5")
ax.grid(True, alpha=0.2)

# typy radarów
kolory = {"A": "#2196F3", "B": "#FF9800"}

# range
for i, k in postawione:
    cx, cy = lokalizacje[i]
    r = typy_radarow[k]
    kolor = kolory[k]
    okrag = plt.Circle((cx, cy), r, color=kolor, alpha=0.15, linewidth=0)
    ax.add_patch(okrag)
    okrag_border = plt.Circle((cx, cy), r, fill=False, color=kolor, linewidth=1.5, linestyle="--", alpha=0.6)
    ax.add_patch(okrag_border)

# lokalizacje ∆
for i, (lx, ly) in enumerate(lokalizacje):
    czy_uzyty = any(ii == i for ii, _ in postawione)
    if czy_uzyty:
        k_typ = next(k for ii, k in postawione if ii == i)
        kolor = kolory[k_typ]
        ax.scatter(lx, ly, s=150, marker="^", c=kolor, zorder=5, edgecolors="black", linewidth=1)
        ax.annotate(f"L{i}({k_typ})", (lx, ly), xytext=(5, 5), textcoords="offset points", fontsize=8, fontweight="bold", color=kolor)
    else:
        ax.scatter(lx, ly, s=60, marker="^", c="#cccccc", zorder=4, edgecolors="#999999", linewidth=0.8)
        ax.annotate(f"L{i}", (lx, ly), xytext=(4, 4), textcoords="offset points", fontsize=7, color="#aaaaaa")

# cele (* = pokryte, o = niepokryte)
for j, (tx, ty) in enumerate(cele):
    w = wagi[j]
    if j in pokryte:
        ax.scatter(tx, ty, s=w * 30 + 40, marker="*", c="#2ecc71", zorder=6, edgecolors="#1a8a4a", linewidth=1)
    else:
        ax.scatter(tx, ty, s=w * 20 + 30, marker="o", c="#e74c3c", zorder=6, edgecolors="#8b0000", linewidth=1, alpha=0.75)
    ax.annotate(f"w={w}", (tx, ty), xytext=(4, 4), textcoords="offset points", fontsize=7.5, color="#333")

# opisy
from matplotlib.lines import Line2D
legenda = [
    Line2D([0], [0], marker="*",  color="w", markerfacecolor="#2ecc71", markersize=12, markeredgecolor="#1a8a4a", label="Cel pokryty"),
    Line2D([0], [0], marker="o",  color="w", markerfacecolor="#e74c3c", markersize=10, markeredgecolor="#8b0000", label="Cel niepokryty"),
    Line2D([0], [0], marker="^",  color="w", markerfacecolor="#2196F3", markersize=10, markeredgecolor="black",   label=f"Radar A (zasięg {typy_radarow['A']})"),
    Line2D([0], [0], marker="^",  color="w", markerfacecolor="#FF9800", markersize=10, markeredgecolor="black",   label=f"Radar B (zasięg {typy_radarow['B']})"),
    Line2D([0], [0], marker="^",  color="w", markerfacecolor="#cccccc", markersize=9,  markeredgecolor="#999999", label="Lokalizacja (nieużyta)"),
]
ax.legend(handles=legenda, loc="upper left", fontsize=8.5, framealpha=0.9)

max_waga = sum(wagi)
ax.set_title(
    f"WMCP — wynik solvera ILP\n"
    f"funkcja celu: {obj:.0f} / {max_waga}  |  "
    f"radarów: {len(postawione)}  |  "
    f"pokrytych celów: {len(pokryte)} / {len(cele)}",
    fontsize=11
)
ax.set_xlabel("x"); ax.set_ylabel("y")

plt.tight_layout()
plt.savefig("mapa.png", dpi=150)
plt.show()
print("zapisano mapa.png")