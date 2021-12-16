import numpy as np
import folium
import json
import branca
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

# ===============================
# OBTENER DATOS DE BASE DE DATOS COMO DATAFRAME
# ===============================

@st.cache(suppress_st_warning = True)
def get_DBData():

    # Conexión con base de datos
    # Argumento: 'mysql+mysqlconnector://[user]:[pass]@[host]:[port]/[schema]'
    engine = create_engine('mysql+mysqlconnector://test:test123@db:3306/test')

    # Se extrae todo el dataset
    dataset = pd.read_sql(
        """
        SELECT covd.*, coud.continent, coud.population
        FROM covid_data covd
        LEFT JOIN country_data coud ON coud.name = covd.country_region
        """,
        con = engine
    )

    return dataset

# ===============================
# LINK CAPA Y ELEMENTO FOLIUM
# ===============================

from branca.element import MacroElement
from jinja2 import Template

class BindColormap(MacroElement):
    """Binds a colormap to a given layer.

    Parameters
    ----------
    colormap : branca.colormap.ColorMap
        The colormap to bind.
    """
    def __init__(self, layer, colormap):
        super(BindColormap, self).__init__()
        self.layer = layer
        self.colormap = colormap
        self._template = Template(u"""
        {% macro script(this, kwargs) %}
            {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
            {{this._parent.get_name()}}.on('overlayadd', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
                }});
            {{this._parent.get_name()}}.on('overlayremove', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'none';
                }});
        {% endmacro %}
        """)  # noqa

# ===============================
# PROCESAR DATOS PARA MAPA
# ===============================

def process_folium_map_data(dataset, sel_date = "2021-05-22"):
    """
    Toma datos preprocesados de COVID y los despliega de manera legible
    dentro de un mapa propio de folium.


    Args:
        dataset (df): Datos obtenidos de la base de datos central de MySQL,
        los cuales son previamente cargados utilizando Airflow.
        sel_date (str, optional): Fecha para la que se van a desplegar resultados.
        Defaults to "2021-05-22".

    Returns:
        folium.map: Mapa de folium con todos sus elementos respectivos listos para
        ser presentados utilizando "folium_static()".
    """


    # Algunos nombres que aparecen como paises en el archivo GeoJson descargado
    # aparecen como "Estado/Provincia" en el dataset principal. Aquí se hace el mapeo,
    # para que el "Estado/Provincia" ahora aparezca como el nombre de país.
    map_state_geoJson = {
        "Greenland": "Greenland",
        "New Caledonia": "New Caledonia",
        "Faroe Islands": "Faroe Islands",
        "Falkland Islands (Malvinas)": "Falkland Islands",
        "Montserrat": "Montserrat",
        "British Virgin Islands": "British Virgin Islands",
        "St Martin": "Saint Martin",
        "Sint Maarten": "Sint Maarten",
        "Saint Barthelemy": "Saint Barthelemy",
        "Anguilla": "Anguilla",
        "Turks and Caicos Islands": "Turks and Caicos Islands",
        "Cayman Islands": "Cayman Islands",
        "Bermuda": "Bermuda",
        "Isle of Man": "Isle of Man"
    }

    for key in map_state_geoJson:
        dataset.loc[dataset["province_state"] == key, "country_region"] = map_state_geoJson[key]

    # Group por país y fecha
    GroupedData = (dataset[dataset["date"] == sel_date]
            .groupby(by = "country_region")
            .sum()
            .reset_index()
    ) 

    # Algunos paises en el GeoJson están escritos diferente con respecto
    # a los datos del dataset. Aquí se hace el mapeo para que ambos nombres
    # sean iguales.
    map_country_geoJson = {
        "US": "United States of America",
        "Burma": "Myanmar",
        "Bahamas": "The Bahamas",
        "Cabo Verde": "Cape Verde",
        "Congo (Brazzaville)": "Republic of Congo",
        "Congo (Kinshasa)": "Democratic Republic of the Congo",
        "Cote d'Ivoire": "Ivory Coast",
        "Czechia": "Czech Republic",
        "Eswatini": "Swaziland", 
        "Korea, South": "South Korea",
        "North Macedonia": "Macedonia",
        "Taiwan*": "Taiwan",
        "Serbia": "Republic of Serbia",
        "Timor-Leste": "East Timor",
        "Tanzania": "United Republic of Tanzania",
        "Holy See": "Vatican",
        "West Bank and Gaza": "Palestine",
        "Guinea-Bissau": "Guinea Bissau",
        "Micronesia": "Federated States of Micronesia"
    }

    for key in map_country_geoJson:
        GroupedData.loc[GroupedData["country_region"] == key, "country_region"] = map_country_geoJson[key]

    # --------------
    # Datos por fecha sin "groupby"
    # --------------

    # Extracción de datos de día específico
    unGroupedData = (dataset[dataset["date"] == sel_date]) 

    # Creación de columna de País + Estado. 
    # Valores iniciales: Nombres de país
    unGroupedData.loc[:,"region_and_province"] = unGroupedData["country_region"]

    # Se agrega "Pais, Estado" a las regiones que cuentan con "provincia_estado"
    region_and_province = unGroupedData.loc[~unGroupedData["province_state"].isna(), "country_region"] + ", " + unGroupedData.loc[~unGroupedData["province_state"].isna(), "province_state"]
    unGroupedData.loc[~unGroupedData["province_state"].isna(), "region_and_province"] = region_and_province

    # Se eliminan las columnas con latitudes y longitudes nulas
    unGroupedData = unGroupedData.dropna(subset = ["lat", "lon"])

    # --------------
    # Settings Markers 
    # --------------

    # Cuantos diferentes tamaños de burbuja van a haber
    size_groups = 8

    # Se calcula el factor de escalado para cada marcador
    # Pasos:
    #   1. Se obtiene la posición en la que se encuentra cada dato (Si USA tiene 33,000 contagiados 
    #      y se usa un size_group de 8, si USA tiene el número más alto de contagiados, su posición
    #      va a ser 0)
    #   2. Para que las posiciones inicien en 1, se le suma 1
    #   3. Se dividen todas las posiciones dentro del número máximo de grupos para obtener un número 
    #      entre 0 y 1.
    unGroupedData["marker_size"] = (pd.qcut(unGroupedData['confirmed'], q = size_groups, labels = False) + 1) / size_groups

    # --------------
    # Edición GeoJson
    # --------------

    # Carga de datos de GeoJson
    with open("./streamlit/countries.geojson") as f:
        geojson_countries = json.load(f)

    # Se le agregan propiedades al JSON
    for i in geojson_countries['features']:

        # Se agrega la feature "id" y la propiedad "Country"
        i['id'] = i['properties']['ADMIN']
        i['properties']["Country"] = i['id']

        # Se agrega la propiedad "Confirmed" al GeoJson
        # (Si el match es nulo, se coloca un 0 en la propiedad)
        match_confirmed = GroupedData.loc[GroupedData["country_region"] == i["id"], "confirmed"].values

        if len(match_confirmed) != 0:
            i['properties']["Confirmed"] = int(match_confirmed[0])
        else:
            i['properties']["Confirmed"] = 0

        # Se agrega la propiedad "Deaths" al GeoJson
        # (Si el match es nulo, se coloca un 0 en la propiedad)
        match_deaths = GroupedData.loc[GroupedData["country_region"] == i["id"], "deaths"].values

        if len(match_deaths) != 0:
            i['properties']["Deaths"] = int(match_deaths[0])
        else:
            i['properties']["Deaths"] = 0

        # Se agrega la propiedad "Recovered" al GeoJson
        # (Si el match es nulo, se coloca un 0 en la propiedad)
        match_recovered = GroupedData.loc[GroupedData["country_region"] == i["id"], "recovered"].values

        if len(match_recovered) != 0:
            i['properties']["Recovered"] = int(match_recovered[0])
        else:
            i['properties']["Recovered"] = 0

    # --------------
    # Folium Map
    # --------------

    # Creación de mapa base
    map = folium.Map(
        location=[0, 0],            # Mapa inicia centrado
        zoom_start = 2,             # Mapa inicia con tres scrolls de zoom
        min_zoom = 2,               # No se puede hacer zoom-out por arriba del valor inicial
        control_scale = True,       # Controles para hacer zoom activados
        max_bounds = True,          # No se puede hacer scroll fuera de los límites
        min_lat = -60)              # No se puede bajar para ver la antartida

    # Bins: Valores límites para agrupar el número de casos
    # Se convierten a float para que el mapa choropleth lo tome correctament
    choropleth_bins = [0, 50, 500, 50000, 500000, 5000000, max(unGroupedData["confirmed"])]
    choropleth_bins = [float(x) for x in choropleth_bins]

    # ======================
    # Confirmed: Choropleth

    # Se convierten a float los bins en los que se va a dividir el número de casos
    confirmed_bins = [0, 50, 500, 50000, 500000, 5000000, max(unGroupedData["confirmed"])]
    confirmed_bins = [float(x) for x in confirmed_bins]

    # Creación de choropleth
    choropleth_confirmed = folium.Choropleth(
        geo_data = geojson_countries,
        name = "Confirmed by Country",
        data = GroupedData,
        columns = ["country_region", "confirmed"],
        key_on = "feature.id",
        fill_color = "BuPu",
        fill_opacity = 0.7,
        line_opacity = 0.5,
        legend_name = "Confirmed Cases",
        highlight = True, 
        bins = confirmed_bins,
        show = False
    )

    # Se elimina la leyenda creada por defecto por choropleth
    for key in choropleth_confirmed._children:
        if key.startswith('color_map'):
            del(choropleth_confirmed._children[key])

    # Se agrega el choropleth luego de eliminar la leyenda
    choropleth_confirmed.add_to(map)

    # Colormap logarítmico para confirmados
    bins_log = np.log(np.array(confirmed_bins) + 1)
    colormap_confirmed = branca.colormap.linear.BuPu_08.scale(0, 500)
    colormap_confirmed = colormap_confirmed.to_step(index = bins_log)
    colormap_confirmed.caption = 'Log(Confirmed)'
    colormap_confirmed.add_to(map)

    # ===================
    # Muertes: Choropleth

    # Se convierten a float los bins en los que se va a dividir el número de casos
    death_bins = [0, 50, 500, 50000, 500000, max(unGroupedData["deaths"])]
    death_bins = [float(x) for x in death_bins]

    # Creación de choropleth
    choropleth_deaths = folium.Choropleth(
        geo_data = geojson_countries,
        name = "Deaths by Country",
        data = GroupedData,
        columns = ["country_region", "deaths"],
        key_on = "feature.id",
        fill_color = "YlOrRd",
        fill_opacity = 0.7,
        line_opacity = 0.5,
        legend_name = "Deaths",
        highlight = True, 
        bins = death_bins,
        show = False
    )

    # Se elimina la leyenda creada por defecto por choropleth
    for key in choropleth_deaths._children:
        if key.startswith('color_map'):
            del(choropleth_deaths._children[key])

    # Se agrega el choropleth luego de eliminar la leyenda
    choropleth_deaths.add_to(map)

    # Colormap logarítmico de muertes
    bins_log = np.log(np.array(death_bins) + 1)
    colormap_deaths = branca.colormap.linear.YlOrRd_09.scale(0, 500)
    colormap_deaths = colormap_deaths.to_step(index = bins_log)
    colormap_deaths.caption = 'Log(Deaths)'
    colormap_deaths.add_to(map)

    # ===================
    # Recuperados: Choropleth

    # Se convierten a float los bins en los que se va a dividir el número de casos
    recovered_bins = [0, 50, 500, 50000, 500000, 5000000, max(unGroupedData["recovered"])]
    recovered_bins = [float(x) for x in recovered_bins]

    choropleth_recovered = folium.Choropleth(
        geo_data = geojson_countries,
        name = "Recovered by Country",
        data = GroupedData,
        columns = ["country_region", "recovered"],
        key_on = "feature.id",
        fill_color = "Greens",
        fill_opacity = 0.7,
        line_opacity = 0.5,
        legend_name = "Recovered",
        highlight = True, 
        bins = recovered_bins,
        show = True
    )

    # Se elimina la leyenda creada por defecto por choropleth
    for key in choropleth_recovered._children:
        if key.startswith('color_map'):
            del(choropleth_recovered._children[key])

    # Se agrega el choropleth luego de eliminar la leyenda
    choropleth_recovered.add_to(map)

    # Colormap logarítmico de recuperados
    bins_log = np.log(np.array(recovered_bins) + 1)
    colormap_recovered = branca.colormap.linear.Greens_08.scale(0, 500)
    colormap_recovered = colormap_recovered.to_step(index = bins_log)
    colormap_recovered.caption = 'Log(Recovered)'
    colormap_recovered.add_to(map)

    # ===================

    # Se crea una capa para todos los marcadores circulares
    feature_group = folium.FeatureGroup(name = "Cases by Region")

    # Para cada pareja de latitud y longitud se crea un marcador circular
    unGroupedData.apply(lambda row: 
        folium.CircleMarker(
            location = [row["lat"], row["lon"]], 
            radius = row["marker_size"] * 12, 
            color = "#3186cc",
            fill = True,
            fill_color = "#3186cc",
            popup = folium.Popup(
                folium.IFrame(
                    f'''<h4 style="font-family: Arial">{row["region_and_province"]}</h4>
                    <p style="font-family: Arial">
                    <b>Confirmed</b>: {"{:,}".format(row["confirmed"])}<br>
                    <b>Deaths</b>: {"{:,}".format(row["deaths"])}<br>
                    <b>Recovered</b>: {"{:,}".format(int(row["recovered"])) if np.isnan(row["recovered"]) == False else 0}<br>
                    </p>
                    '''
                ), 
                min_width=250,
                max_width=250
            )     
        ).add_to(feature_group),
        axis = 1)

    # Se agregan todos los puntos al mapa como una capa
    feature_group.add_to(map)

    # Mantener al frente las burbujitas siempre
    map.keep_in_front(feature_group)

    # Popup para cada choroplath
    folium.features.GeoJsonPopup(fields = ["Country", "Confirmed"]).add_to(choropleth_confirmed.geojson)
    folium.features.GeoJsonPopup(fields = ["Country", "Deaths"]).add_to(choropleth_deaths.geojson)
    folium.features.GeoJsonPopup(fields = ["Country", "Recovered"]).add_to(choropleth_recovered.geojson)

    # Control de capa para apagar o encender el mapa de choropleth
    folium.LayerControl().add_to(map)

    # Adición de mini-mapa
    from folium import plugins
    minimap = plugins.MiniMap(toggle_display=True)
    map.add_child(minimap)

    # Se crea un link entre cada colorbar y el choropleth
    map.add_child(BindColormap(choropleth_confirmed, colormap_confirmed))
    map.add_child(BindColormap(choropleth_deaths, colormap_deaths))
    map.add_child(BindColormap(choropleth_recovered, colormap_recovered))

    # Nota: El mapa generado es bastante grande
    # Dependiendo del tamaño se deberán modificar los límites de tamaño de elementos estáticos
    # de streamlit en el dockerfile correspondiente de acuerdo a lo dicho en el siguiente foro: 
    # https://discuss.streamlit.io/t/runtimeerror-data-of-size-107-9mb-exceeds-write-limit-of-50-0mb/6970/13

    return (map)