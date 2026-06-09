import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from dane import lokalizacje, cele, wagi, typy_radarow

def rysuj_mape(wynik_dict, nazwa_pliku="mapa.png"):
    # Pobieranie danych ze słownika wygenerowanego przez algorytm
    postawione = wynik_dict["postawione"]
    pokryte = wynik_dict["pokryte"]
    obj = wynik_dict["obj"]
    czas = wynik_dict["czas"]
    algorytm = wynik_dict["algorytm"]

    # Konfiguracja głównego okna mapy
    fig, ax = plt.subplots(figsize=(9, 8))
    ax.set_xlim(0, 10000)
    ax.set_ylim(0, 10000)
    ax.set_aspect("equal")
    ax.set_facecolor("#f5f5f5")
    ax.grid(True, alpha=0.2)

    # Dynamiczna paleta kolorów, by obsłużyć radary A, B oraz ewentualne C, D...
    paleta = ["#2196F3", "#FF9800", "#9C27B0", "#4CAF50", "#E91E63"]
    kolory = {k: paleta[i % len(paleta)] for i, k in enumerate(typy_radarow.keys())}

    # 1. Rysowanie zasięgów (okręgów)
    for i, k in postawione:
        cx, cy = lokalizacje[i]
        r = typy_radarow[k]
        kolor = kolory[k]
        
        # Wypełnienie z przezroczystością
        okrag = plt.Circle((cx, cy), r, color=kolor, alpha=0.15, linewidth=0)
        ax.add_patch(okrag)
        # Przerywana obwódka
        okrag_border = plt.Circle((cx, cy), r, fill=False, color=kolor, linewidth=1.5, linestyle="--", alpha=0.6)
        ax.add_patch(okrag_border)

    # 2. Rysowanie lokalizacji (trójkąty)
    for i, (lx, ly) in enumerate(lokalizacje):
        # Sprawdzamy, czy w tej lokalizacji coś stoi
        czy_uzyty = any(ii == i for ii, _ in postawione)
        if czy_uzyty:
            k_typ = next(k for ii, k in postawione if ii == i)
            kolor = kolory[k_typ]
            ax.scatter(lx, ly, s=150, marker="^", c=kolor, zorder=5, edgecolors="black", linewidth=1)
            ax.annotate(f"L{i}({k_typ})", (lx, ly), xytext=(5, 5), textcoords="offset points", fontsize=8, fontweight="bold", color=kolor)
        else:
            # Lokalizacja pusta
            ax.scatter(lx, ly, s=60, marker="^", c="#cccccc", zorder=4, edgecolors="#999999", linewidth=0.8)
            ax.annotate(f"L{i}", (lx, ly), xytext=(4, 4), textcoords="offset points", fontsize=7, color="#aaaaaa")

    # 3. Rysowanie celów (gwiazdki pokryte, kółka niepokryte)
    for j, (tx, ty) in enumerate(cele):
        w = wagi[j]
        if j in pokryte:
            ax.scatter(tx, ty, s=w * 30 + 40, marker="*", c="#2ecc71", zorder=6, edgecolors="#1a8a4a", linewidth=1)
        else:
            ax.scatter(tx, ty, s=w * 20 + 30, marker="o", c="#e74c3c", zorder=6, edgecolors="#8b0000", linewidth=1, alpha=0.75)
        # Opis wagi obok celu
        ax.annotate(f"w={w}", (tx, ty), xytext=(4, 4), textcoords="offset points", fontsize=7.5, color="#333")

    # 4. Automatyczna legenda
    legenda = [
        Line2D([0], [0], marker="*", color="w", markerfacecolor="#2ecc71", markersize=12, markeredgecolor="#1a8a4a", label="Cel pokryty"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#e74c3c", markersize=10, markeredgecolor="#8b0000", label="Cel niepokryty")
    ]
    # Dodajemy do legendy wszystkie typy radarów istniejące w pliku dane.py
    for k in typy_radarow.keys():
        legenda.append(Line2D([0], [0], marker="^", color="w", markerfacecolor=kolory[k], markersize=10, markeredgecolor="black", label=f"Radar {k} (zasięg {typy_radarow[k]})"))
        
    legenda.append(Line2D([0], [0], marker="^", color="w", markerfacecolor="#cccccc", markersize=9, markeredgecolor="#999999", label="Lokalizacja (nieużyta)"))
    ax.legend(handles=legenda, loc="upper left", fontsize=8.5, framealpha=0.9)

    # 5. Tytuł z podsumowaniem wyników
    max_waga = sum(wagi)
    ax.set_title(
        f"WMCP — Wynik: {algorytm}\n"
        f"Zysk: {obj:.0f} / {max_waga}  |  Czas: {czas:.3f} s  |  "
        f"Postawione radary: {len(postawione)}",
        fontsize=11
    )
    ax.set_xlabel("Współrzędna X")
    ax.set_ylabel("Współrzędna Y")

    # Zapis i zamykanie
    plt.tight_layout()
    plt.savefig(nazwa_pliku, dpi=150)
    plt.close() # Ekstremalnie ważne przy uruchamianiu w pętli – zwalnia pamięć!