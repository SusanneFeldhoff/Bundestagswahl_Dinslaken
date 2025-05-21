
# 🗳️ Bundestagswahlergebnisse Dinslaken 2025

Diese interaktive Streamlit-App visualisiert die Wahlergebnisse der Bundestagswahl 2025 in Dinslaken – sowohl auf Bezirksebene als auch nach Parteistärke.

## 🔍 Funktionen

- **Siegerpartei pro Stimmbezirk** (Erst- und Zweitstimme)
- **Bester Stimmbezirk pro Partei im Bundestag**
- **Komplettdarstellung pro Partei** mit farblicher Abstufung je nach Stimmenanteil
- **Interaktive Karte mit Pop-ups & Screenshots** der Wahlkreisergebnisse
- **Filter nach Stimme und Partei**
- **Farblegende & Tooltips**

## 📦 Technologien

- [Streamlit](https://streamlit.io)
- [Folium](https://python-visualization.github.io/folium/)
- [GeoPandas](https://geopandas.org/)
- [Pandas](https://pandas.pydata.org/)
- [branca](https://python-visualization.github.io/branca/) für Farbskalen

## 🚀 Online ausprobieren

👉 **[Hier geht’s zur App](https://bundestagswahldinslaken.streamlit.app/)**


## 🗂️ Projektstruktur

```bash
├── Wahl.py                  # Hauptdatei für die Streamlit-App
├── requirements.txt         # Paketabhängigkeiten
├── Data/
│   ├── gdf_merged_final.geojson
│   ├── best_result_1_ohneBW.csv
│   └── best_result_2_ohneBW.csv
├── images/                  # Screenshots zur Visualisierung
└── README.md
