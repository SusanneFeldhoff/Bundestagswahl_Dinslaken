import streamlit as st
st.set_page_config(layout="wide")  # Muss ganz oben stehen

import geopandas as gpd
import folium
from streamlit_folium import folium_static
import base64
from pathlib import Path
from shapely.geometry import shape
import pandas as pd
from branca.colormap import linear, LinearColormap

# === Farben definieren ===
color_map = {
    "CDU": "#000000",
    "SPD": "#FF0000",
    "GRÜNE": "#008000",
    "AfD": "#0000FF",
    "Die Linke": "#800080",
    "Team Toden": "#FFA500",
    "MLPD": "#00FFFF",
}

# === Bild als base64 laden ===
def image_to_base64(rel_path):
    try:
        base_path = Path(__file__).parent
        full_path = base_path / rel_path
        if not full_path.exists():
            st.warning(f"❌ Bild nicht gefunden: {full_path}")
            return None
        with open(full_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception as e:
        st.error(f"Fehler beim Laden von {rel_path}: {e}")
        return None

# === Popup HTML erzeugen (mit Scrollbar) ===
def popup_html(props):
    gemeinde = props.get("GEMEINDE", "n/a")
    bezirk = props.get("BEZIRKSNUMMER", "n/a")

    pfad_erst = props.get("Pfad_Erststimme", "")
    pfad_zweit = props.get("Pfad_Zweitstimme", "")

    img_erst = "<p>Kein Screenshot (Erststimme)</p>"
    img_zweit = "<p>Kein Screenshot (Zweitstimme)</p>"

    if pfad_erst:
        b64 = image_to_base64(pfad_erst)
        if b64:
            img_erst = f'<img src="data:image/png;base64,{b64}" width="600">'

    if pfad_zweit:
        b64 = image_to_base64(pfad_zweit)
        if b64:
            img_zweit = f'<img src="data:image/png;base64,{b64}" width="600">'

    return f"""
    <div style='width: 700px; height: 500px; overflow-y: auto;'>
        <b>Gemeinde:</b> {gemeinde} | <b>Bezirk:</b> {bezirk}<br><br>
        <b>Erststimme</b><br>{img_erst}<br><br>
        <b>Zweitstimme</b><br>{img_zweit}
    </div>
    """

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
        Ergebnisse der Bundestagswahl 2025 für Dinslaken
    </h1>
    <hr style='margin-top: 0;'>
""", unsafe_allow_html=True)

# === Layout: Spaltenaufteilung ===
col1, col2 = st.columns([1, 3])

with col1:
    wahltyp = st.selectbox("Wähle den Typ der Stimme", ["Erststimme", "Zweitstimme"])
    darstellung = st.radio("Darstellung", [
        "Siegerpartei pro Stimmbezirk",
        "Bester Stimmbezirk pro Bundestagspartei",
        "Komplettdarstellung pro Bundestagspartei"
    ])

    bundestagsparteien = ["CDU", "SPD", "GRÜNE", "AfD", "Die Linke"]
    partei_auswahl = st.selectbox("Wähle eine Partei", bundestagsparteien) if darstellung == "Komplettdarstellung pro Bundestagspartei" else None

with col2:
    m = folium.Map(location=[51.564, 6.733], zoom_start=12)

    if darstellung == "Siegerpartei pro Stimmbezirk":
        spalte = "SIEGERPARTEI_Erst" if wahltyp == "Erststimme" else "SIEGERPARTEI_Zweit"
        for _, row in gdf_merged.iterrows():
            partei = row.get(spalte, "")
            farbe = color_map.get(partei, "#CCCCCC")
            popup = folium.Popup(popup_html(row), max_width=750)

            folium.GeoJson(
                row["geometry"].__geo_interface__,
                style_function=lambda feature, farbe=farbe: {
                    "fillColor": farbe,
                    "color": "black",
                    "weight": 1,
                    "fillOpacity": 0.7
                },
                tooltip=f"Bezirk {row['BEZIRKSNUMMER']} — {partei}"
            ).add_child(popup).add_to(m)

    elif darstellung == "Bester Stimmbezirk pro Bundestagspartei":
        result_df = lade_ergebnisse(wahltyp)

        folium.GeoJson(
            data=gdf_merged,
            style_function=lambda feature: {
                "fillColor": "#eeeeee",
                "color": "#999999",
                "weight": 1,
                "fillOpacity": 0.2
            }
        ).add_to(m)

        for partei in bundestagsparteien:
            df_p = result_df[result_df["Partei"] == partei]
            if df_p.empty:
                continue
            best_row = df_p.sort_values("Ergebnis", ascending=False).iloc[0]
            bezirk = best_row["BEZIRKSNUMMER"]
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

    elif darstellung == "Komplettdarstellung pro Bundestagspartei" and partei_auswahl:
        spaltenname = f"{partei_auswahl}_{'1' if wahltyp == 'Erststimme' else '2'} %"
        if spaltenname not in gdf_merged.columns:
            st.error(f"Spalte {spaltenname} nicht gefunden.")
        else:
            farbskalen = {
                "SPD": "YlOrRd",
                "GRÜNE": "Greens",
                "AfD": "Blues",
                "Die Linke": "PuRd",
            }

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
                    name="CDU",
                    style_function=style_function,
                    tooltip=folium.GeoJsonTooltip(
                        fields=["BEZIRKSNUMMER", spaltenname],
                        aliases=["Bezirk:", f"{partei_auswahl} (%):"]
                    )
                ).add_to(m)

                colormap.caption = f"{partei_auswahl}-Stimmenanteil (%)"
                colormap.add_to(m)

            else:
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
                    tooltip=folium.GeoJsonTooltip(
                        fields=["BEZIRKSNUMMER", spaltenname],
                        aliases=["Bezirk:", f"{partei_auswahl} (%):"]
                    )
                ).add_to(m)

    folium.LayerControl().add_to(m)
    folium_static(m, width=1150, height=700)



