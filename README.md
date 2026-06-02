# WMCP — Weighted Maximum Coverage Problem
### Podstawy Decision Making | Projekt zaliczeniowy

---

## Problem

Na obszarze geograficznym rozmieszczone są obiekty o różnej wadze strategicznej
(bazy, lotniska, elektrownie). Dysponujemy budżetem **N radarów** które możemy
postawić w predefiniowanych lokalizacjach. Każdy typ radaru ma inny zasięg.

**Cel:** zmaksymalizować łączną wagę strategiczną obiektów objętych zasięgiem
co najmniej jednego radaru.

**Klasa problemu:** NP-trudny (Weighted Maximum Coverage Problem)


### Uruchomienie solver2.py (GUI do zmiany parametrów problemu)

pip install streamlit

python3 -m streamlit run solver2.py