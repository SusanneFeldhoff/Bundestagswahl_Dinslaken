# 🗳️ Bundestagswahlergebnisse Dinslaken 2025

Diese interaktive Streamlit-App visualisiert die Wahlergebnisse der Bundestagswahl 2025 in Dinslaken – sowohl auf Bezirksebene als auch nach Parteistärke.

## 🔍 Funktionen

- **Siegerpartei pro Stimmbezirk** (für Erst- und Zweitstimme)
- **Bester Stimmbezirk pro Partei im Bundestag** (Top-Ergebnis farblich hervorgehoben)
- **Komplettdarstellung pro Partei im Bundestag** mit Choroplethen (farbliche Abstufung je nach Stimmenanteil)
- **Wahlbeteiligung pro Stimmbezirk** für Erst- und Zweitstimme
- **Parallele Kartenansicht** für Erst- und Zweitstimme nebeneinander
- **Tooltips mit Ergebnisübersicht** je Stimmbezirk (inkl. aller relevanten Parteien)
- **Filter nach Stimme, Partei und Darstellungsart**
- **Farblegende & interaktive Hover-Tooltips**
- 🔗 **Externer Link zur Detailauswertung beim KRZN**

## 📦 Technologien

- [Streamlit](https://streamlit.io)
- [Folium](https://python-visualization.github.io/folium/)
- [GeoPandas](https://geopandas.org/)
- [Pandas](https://pandas.pydata.org/)
- [branca](https://python-visualization.github.io/branca/) (für Farbskalen und Legenden)

## 📚 Quellen

- 🔗 Wahlergebnisse, Screenshots und WFS: [Zweckverband Kommunales Rechenzentrum Niederrhein (KRZN)](https://wahl.krzn.de/bw2025/wep310/navi/310-305-BW-STMM-1.html)
- 📎 GeoJSON-Daten: Eigene Aufbereitung auf Basis kommunaler Wahldaten

## 🚀 Online ausprobieren

👉 **[Hier geht’s zur App](https://bundestagswahldinslaken.streamlit.app/)**

## 🗂️ Projektstruktur

```bash
├── Wahl.py                     # Hauptdatei für die Streamlit-App
├── requirements.txt            # Paketabhängigkeiten
├── Data/
│   ├── gdf_merged_final.geojson
│   ├── best_result_1_ohneBW.csv
│   └── best_result_2_ohneBW.csv
├── images/                     # Screenshots pro Stimmbezirk
└── README.md
