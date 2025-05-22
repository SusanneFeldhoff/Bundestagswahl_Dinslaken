import streamlit as st
st.set_page_config(layout="wide")  # Muss ganz oben stehen

import geopandas as gpd
import folium
from streamlit_folium import folium_static
from pathlib import Path
import pandas as pd
from branca.colormap import LinearColormap
from folium.features import GeoJsonTooltip

# === Farben definieren ===
color_map = {
    "CDU": "#000000",
    "SPD": "#FF0000",
    "GRÜNE": "#008000",
    "AfD": "#0000FF",
    "Die Linke": "#800080",
    "Team Toden": "#FFA500",
    "MLPD": "#00FFFF",
    "BSW": "#9932CC",
    "FDP": "#FFFF00"
}

# Nur die Bundestagsparteien definieren
bundestagsparteien = ["CDU", "SPD", "GRÜNE", "AfD", "Die Linke"]

# === Daten laden ===
@st.cache_data
def lade_geodaten():
    return gpd.read_file(Path(__file__).parent / "Data" / "gdf_merged_final.geojson")

@st.cache_data
def lade_ergebnisse(wahltyp):
    dateiname = "best_result_1_ohneBW.csv" if wahltyp == "Erststimme" else "best_result_2_ohneBW.csv"
    return pd.read_csv(Path(__file__).parent / "Data" / dateiname)

gdf_merged = lade_geodaten()

# === Header anzeigen ===
st.markdown("""
    <h1 style='text-align: center; margin-bottom: 0;'>
        Wahlergebnisse Dinslaken 2025
    </h1>
    <hr style='margin-top: 0;'>
    <p style='text-align: center;'>🔗 Weitere Infos zu den Ergebnissen: <a href='https://wahl.krzn.de/bw2025/wep310/navi/310-305-BW-STMM-1.html' target='_blank'>wahl.krzn.de</a></p>
""", unsafe_allow_html=True)

# === Layout mit zwei Spalten oben für Steuerung ===
steuerung_col1, steuerung_col2 = st.columns([3, 2])

with steuerung_col1:
    darstellung = st.radio("Darstellung", [
        "Siegerpartei pro Stimmbezirk",
        "Bester Stimmbezirk pro Partei im Bundestag",
        "Komplettdarstellung pro Partei im Bundestag",
        "Wahlbeteiligung pro Stimmbezirk"
    ])

with steuerung_col2:
    partei_auswahl = st.selectbox("Wähle eine Partei", bundestagsparteien + ["BSW", "FDP"]) if darstellung == "Komplettdarstellung pro Partei im Bundestag" else None

# === Parallele Kartenansicht für Erst- und Zweitstimme ===
col1, col2 = st.columns(2)

# === Siegerpartei pro Stimmbezirk ===
if darstellung == "Siegerpartei pro Stimmbezirk":
    partei_tooltip_felder = [
        "SPD_{} %", "CDU_{} %", "GRÜNE_{} %", "AfD_{} %", "Die Linke_{} %", "FDP_{} %", "BSW_{} %"
    ]
    for stimme, col in zip(["Erststimme", "Zweitstimme"], [col1, col2]):
        stimme_nr = "1" if stimme == "Erststimme" else "2"
        spalte = f"SIEGERPARTEI_{'Erst' if stimme == 'Erststimme' else 'Zweit'}"
        tooltip_fields = [feld.format(stimme_nr) for feld in partei_tooltip_felder if feld.format(stimme_nr) in gdf_merged.columns]
        aliases = [f"{feld.split('_')[0]} (%):" for feld in tooltip_fields]

        with col:
            st.subheader(stimme)
            m = folium.Map(location=[51.564, 6.733], zoom_start=12)

            def style_function_factory(spaltenname):
                def style_function(feature):
                    partei = feature["properties"].get(spaltenname, "")
                    return {
                        "fillColor": color_map.get(partei, "#CCCCCC"),
                        "color": "black",
                        "weight": 1,
                        "fillOpacity": 0.7
                    }
                return style_function

            folium.GeoJson(
                data=gdf_merged.__geo_interface__,
                style_function=style_function_factory(spalte),
                tooltip=GeoJsonTooltip(
                    fields=["BEZIRKSNUMMER"] + tooltip_fields,
                    aliases=["Bezirk:"] + aliases,
                    localize=True
                )
            ).add_to(m)

            folium_static(m, width=600, height=500)

# Nur Bundestagsparteien berücksichtigen bei bester Stimmbezirk pro Partei
elif darstellung == "Bester Stimmbezirk pro Partei im Bundestag":
    parteien_liste = bundestagsparteien
    for stimme, col in zip(["Erststimme", "Zweitstimme"], [col1, col2]):
        result_df = lade_ergebnisse(stimme)
        with col:
            st.subheader(stimme)
            m = folium.Map(location=[51.564, 6.733], zoom_start=12)
            folium.GeoJson(
                data=gdf_merged,
                style_function=lambda feature: {
                    "fillColor": "#eeeeee",
                    "color": "#999999",
                    "weight": 1,
                    "fillOpacity": 0.2
                }
            ).add_to(m)

            best_bezirke = set()
            for partei in parteien_liste:
                df_p = result_df[result_df["Partei"] == partei]
                if df_p.empty:
                    continue
                best_row = df_p.sort_values("Ergebnis", ascending=False).iloc[0]
                bezirk = best_row["BEZIRKSNUMMER"]
                if bezirk in best_bezirke:
                    continue  # Vermeide doppelte Darstellung bei gleichem Bezirk
                best_bezirke.add(bezirk)
                stimmen = best_row["Ergebnis"]
                farbe = color_map.get(partei, "#CCCCCC")
                bezirk_data = gdf_merged[gdf_merged["BEZIRKSNUMMER"] == bezirk]
                if bezirk_data.empty:
                    continue
                geom = bezirk_data.iloc[0].geometry
                folium.GeoJson(
                    geom.__geo_interface__,
                    style_function=lambda feature, farbe=farbe: {
                        "fillColor": farbe,
                        "color": "black",
                        "weight": 2,
                        "fillOpacity": 0.8
                    },
                    tooltip=f"{partei}: {stimmen:.1f}%"
                ).add_to(m)
            folium_static(m, width=600, height=500)

else:
    parteien_liste = list(color_map.keys())

if darstellung == "Wahlbeteiligung pro Stimmbezirk":
    for stimme, col in zip(["Erststimme", "Zweitstimme"], [col1, col2]):
        spaltenname = f"Wahlbeteiligung_{'1' if stimme == 'Erststimme' else '2'} %"
        with col:
            st.subheader(f"{stimme} – Wahlbeteiligung")
            m = folium.Map(location=[51.564, 6.733], zoom_start=12)
            colormap = LinearColormap(
                colors=["#ffffcc", "#a1dab4", "#41b6c4", "#2c7fb8", "#253494"],
                vmin=gdf_merged[spaltenname].min(),
                vmax=gdf_merged[spaltenname].max()
            )

            def style_function(feature):
                wert = feature["properties"].get(spaltenname, 0)
                return {
                    "fillColor": colormap(wert),
                    "color": "black",
                    "weight": 0.5,
                    "fillOpacity": 0.7
                }

            folium.GeoJson(
                data=gdf_merged.__geo_interface__,
                style_function=style_function,
                tooltip=GeoJsonTooltip(
                    fields=["BEZIRKSNUMMER", spaltenname],
                    aliases=["Bezirk:", "Wahlbeteiligung (%):"]
                )
            ).add_to(m)

            colormap.caption = "Wahlbeteiligung (%)"
            colormap.add_to(m)

            folium_static(m, width=600, height=500)

# elif darstellung == "Bester Stimmbezirk pro Partei im Bundestag":
#     parteien_liste = bundestagsparteien
#     for stimme, col in zip(["Erststimme", "Zweitstimme"], [col1, col2]):
#         result_df = lade_ergebnisse(stimme)
#         with col:
#             st.subheader(stimme)
#             m = folium.Map(location=[51.564, 6.733], zoom_start=12)
#             folium.GeoJson(
#                 data=gdf_merged,
#                 style_function=lambda feature: {
#                     "fillColor": "#eeeeee",
#                     "color": "#999999",
#                     "weight": 1,
#                     "fillOpacity": 0.2
#                 }
#             ).add_to(m)

#             for partei in parteien_liste:
#                 df_p = result_df[result_df["Partei"] == partei]
#                 if df_p.empty:
#                     continue
#                 best_row = df_p.sort_values("Ergebnis", ascending=False).iloc[0]
#                 bezirk = best_row["BEZIRKSNUMMER"]
#                 stimmen = best_row["Ergebnis"]
#                 farbe = color_map.get(partei, "#CCCCCC")
#                 bezirk_data = gdf_merged[gdf_merged["BEZIRKSNUMMER"] == bezirk]
#                 if bezirk_data.empty:
#                     continue
#                 geom = bezirk_data.iloc[0].geometry
#                 folium.GeoJson(
#                     geom.__geo_interface__,
#                     style_function=lambda feature, farbe=farbe: {
#                         "fillColor": farbe,
#                         "color": "black",
#                         "weight": 2,
#                         "fillOpacity": 0.8
#                     },
#                     tooltip=f"{partei}: {stimmen:.1f}%"
#                 ).add_to(m)
#             folium_static(m, width=600, height=500)
# else:
#     parteien_liste = list(color_map.keys())


# elif darstellung == "Bester Stimmbezirk pro Partei im Bundestag":
#     for stimme, col in zip(["Erststimme", "Zweitstimme"], [col1, col2]):
#         result_df = lade_ergebnisse(stimme)
#         with col:
#             st.subheader(stimme)
#             m = folium.Map(location=[51.564, 6.733], zoom_start=12)
#             folium.GeoJson(
#                 data=gdf_merged,
#                 style_function=lambda feature: {
#                     "fillColor": "#eeeeee",
#                     "color": "#999999",
#                     "weight": 1,
#                     "fillOpacity": 0.2
#                 }
#             ).add_to(m)
#             for partei in bundestagsparteien:
#                 df_p = result_df[result_df["Partei"] == partei]
#                 if df_p.empty:
#                     continue
#                 best_row = df_p.sort_values("Ergebnis", ascending=False).iloc[0]
#                 bezirk = best_row["BEZIRKSNUMMER"]
#                 stimmen = best_row["Ergebnis"]
#                 farbe = color_map.get(partei, "#CCCCCC")
#                 bezirk_data = gdf_merged[gdf_merged["BEZIRKSNUMMER"] == bezirk]
#                 if bezirk_data.empty:
#                     continue
#                 geom = bezirk_data.iloc[0].geometry
#                 folium.GeoJson(
#                     geom.__geo_interface__,
#                     style_function=lambda feature, farbe=farbe: {
#                         "fillColor": farbe,
#                         "color": "black",
#                         "weight": 2,
#                         "fillOpacity": 0.8
#                     },
#                     tooltip=f"{partei}: {stimmen:.1f}%"
#                 ).add_to(m)
#             folium_static(m, width=600, height=500)

elif darstellung == "Komplettdarstellung pro Partei im Bundestag" and partei_auswahl:
    for stimme, col in zip(["Erststimme", "Zweitstimme"], [col1, col2]):
        spaltenname = f"{partei_auswahl}_{'1' if stimme == 'Erststimme' else '2'} %"
        with col:
            st.subheader(f"{stimme} – {partei_auswahl}")
            m = folium.Map(location=[51.564, 6.733], zoom_start=12)
            if partei_auswahl == "CDU":
                colormap = LinearColormap(
                    colors=["#aaaaaa", "#555555", "#000000"],
                    vmin=gdf_merged[spaltenname].min(),
                    vmax=gdf_merged[spaltenname].max()
                )

                def style_function(feature):
                    wert = feature["properties"].get(spaltenname, 0)
                    return {
                        "fillColor": colormap(wert),
                        "color": "black",
                        "weight": 0.5,
                        "fillOpacity": 0.7,
                    }

                folium.GeoJson(
                    data=gdf_merged.__geo_interface__,
                    name=partei_auswahl,
                    style_function=style_function,
                    tooltip=GeoJsonTooltip(
                        fields=["BEZIRKSNUMMER", spaltenname],
                        aliases=["Bezirk:", f"{partei_auswahl} (%):"]
                    )
                ).add_to(m)
                colormap.caption = f"{partei_auswahl}-Stimmenanteil (%)"
                colormap.add_to(m)
            else:
                farbskalen = {
                    "SPD": "YlOrRd",
                    "GRÜNE": "Greens",
                    "AfD": "Blues",
                    "Die Linke": "PuRd",
                    "FDP": "YlGnBu",
                    "BSW": "BuPu"
                }
                folium.Choropleth(
                    geo_data=gdf_merged,
                    data=gdf_merged,
                    columns=["BEZIRKSNUMMER", spaltenname],
                    key_on="feature.properties.BEZIRKSNUMMER",
                    fill_color=farbskalen.get(partei_auswahl, "YlOrRd"),
                    fill_opacity=0.7,
                    line_opacity=0.5,
                    legend_name=f"{partei_auswahl}-Stimmenanteil (%)"
                ).add_to(m)

                folium.GeoJson(
                    data=gdf_merged.__geo_interface__,
                    tooltip=GeoJsonTooltip(
                        fields=["BEZIRKSNUMMER", spaltenname],
                        aliases=["Bezirk:", f"{partei_auswahl} (%):"]
                    )
                ).add_to(m)
            folium_static(m, width=600, height=500)

else:
    st.info("Diese Ansicht ist nur für die Darstellung der Wahlbeteiligung aktiv.")
