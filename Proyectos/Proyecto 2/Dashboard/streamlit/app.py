import streamlit as st
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from streamlit_folium import folium_static
from functions import process_folium_map_data, get_DBData
from datetime import datetime

# ================
# SETTINGS
# ================

# Elimina el footer y el menú para que la persona que observe el dashboard
# no pueda cambiar nada importante. También esconde el footer con "made with streamlit"
hide_menu_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
#st.markdown(hide_menu_style, unsafe_allow_html=True)

# ================
# TITULO
# ================

# TODO: Navbar - https://discuss.streamlit.io/t/streamlit-navbar/14936/27

# Layout ancho (Similar a una página web tradicional)
st.set_page_config(layout="wide", page_title = "COVID-19 Dashboard", page_icon = ":microscope:")

st.markdown("""
<div class = "banner">
    <h1 style = "margin-left: 20px";>COVID-19 Dashboard</h1>
</div>
<style>
    .banner {
        background-image: linear-gradient(90deg, rgba(72,92,183,1) 56%, rgba(0,212,255,0) 100%);;
        border-radius: 20px 0 0 20px;
        margin-bottom: 50px;
    }
</style>
""", unsafe_allow_html = True)

# ================
# DATASET
# ================

try: 
    dataset = get_DBData()

except Exception as e:
    st.write("Database not yet available.")
    st.image("streamlit/map.PNG")

# ===============
# SIDE BAR
# ===============

st.sidebar.markdown("""
# Map Options
--------
""")

latest_date = dataset['date'].max()
earliest_date = dataset['date'].min()

analysis_date = st.sidebar.date_input(
    'Date for COVID data', 
    value = dataset['date'].max(),
    min_value = earliest_date,
    max_value = latest_date
)

st.sidebar.markdown(f"""
##### Dataset date range: { dataset['date'].min().date().strftime('%m/%d/%Y') } - { dataset['date'].max().date().strftime('%m/%d/%Y') }
------
""")

map_type = st.sidebar.selectbox('Map Type', ('Data by Region', 'Confirmed Cases by Country', 'Deaths by Country', 'Recovered Cases by Country'))

st.sidebar.markdown("""
<ul>
    <li style="font-size: 14px";>Confirmed: Purple Choropleth</li>
    <li style="font-size: 14px";>Deaths: Red Choropleth</li>
    <li style="font-size: 14px";>Recovered: Green Choropleth</li>
    <li style="font-size: 14px";>Data by Region: Bubbles</li>
</ul>
<style>
    ul{margin:0}
    li{line-height:15px}
</style>
<hr>
""", unsafe_allow_html = True)

disable_map = st.sidebar.checkbox("Disable Map", value = True)
st.sidebar.markdown("##### Note: Enable for faster performance")

view_raw_dataset = st.sidebar.checkbox("View Raw Map Data", value = False)
st.sidebar.markdown("##### Enable expander with raw map data")

# ================
# FOLIUM MAP
# ================

# TODO: Mapa animado - https://www.google.com/search?client=opera&q=create+timestamped+geoJSON&sourceid=opera&ie=UTF-8&oe=UTF-8

# Solo se renderiza el mapa si el usuario lo desea
if disable_map == False:

    maps = process_folium_map_data(dataset, analysis_date)

    # Se utiliza el mapa elegido por el usuario
    if map_type == "Data by Region":
        map = maps["bubbles"]
    elif map_type == "Confirmed Cases by Country":
        map = maps["confirmed"]
    elif map_type == "Deaths by Country":
        map = maps["deaths"]
    elif map_type == "Recovered Cases by Country":
        map = maps["recovered"]

    # Se renderiza el mapa
    with st.spinner("Loading Map..."):
        folium_static(map, width = 1420, height = 580)

else:
    st.image("streamlit/map.PNG")

# Pestaña expandible para ver el datset raw
if view_raw_dataset == True:
    with st.expander("Raw Map Data"):
        st.write(dataset[dataset["date"] == analysis_date.strftime('%Y-%m-%d')].reset_index())

# ================
# CONTENT
# ================

import matplotlib.pyplot as plt
import plotly.express as px

# ----------------
# SITUACIÓN GLOBAL
# ----------------
st.markdown("""
<div class = "subsection">
    <h2 class = "subsection-text">  Global Situation  </h2>
</div>
<style>
    .subsection {
        background-color: rgba(72,92,183,1);
        border-radius: 20px;
        margin-bottom: 25px;
        margin-top: 200px;
        display: table;
        max-width: 75%;
        min-width: 30%;
    }
    .subsection-text {
        display: flex;
        justify-content: center;
        align-items: center;
    }
</style>
<hr>
""", unsafe_allow_html = True)

# MÉTRICAS
# ----------------

with st.container():
    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])

    # Se obtiene la data más reciente
    latest_data = dataset[dataset['date'] == latest_date]

    # Se eliminan potenciales NANs
    latest_data[["confirmed", "deaths", "population"]] = latest_data[["confirmed", "deaths", "population"]].fillna(0)

    # Se calcula por aparte el número de recuperados porque el CSV fuente
    # parece perder datos de repente luego de cierta fecha. Parece que luego
    # de un momento específico, cada país dejó de reportar sus recuperados
    total_recovered = dataset[["country_region", "recovered"]].groupby(by = ["country_region"]).max().fillna(0).sum()

    # Creación de métricas
    col1.metric("Total Cases", f"{latest_data['confirmed'].sum() / 1000000:,.0f}M")
    col2.metric("Total Deaths", f"{latest_data['deaths'].sum() / 1000000:,.1f}M")
    col3.metric("Case-Fatality Ratio", f"{(latest_data['deaths'].sum() / latest_data['confirmed'].sum()) * 100:.2f}%")
    col4.metric("Recovery Percentage", f"{(total_recovered.values[0] / latest_data['confirmed'].sum()) * 100:.2f}%")
    col5.metric("Incidence (Cases per 100,000 people)", f"{(latest_data['confirmed'].sum() / latest_data['population'].sum()) * 100000:.0f} cases")
    col6.metric("Most Fatal Country", latest_data.loc[latest_data["deaths"] == latest_data["deaths"].max(), "country_region"].values[0])

st.markdown("-----")

# CASOS CONFIRMADOS
# ----------------
with st.container():
    col1, col2 = st.columns([4, 1])

    # Espacio vacío arriba de los controles
    col2.markdown("""
    #
    ### Controls
    """)

    # Controles
    sequence_type = col2.radio("Sequence Type", ("Cumulative", "Difference"), key = "seq_conf")
    data_freq = col2.radio("Data Frequency", ("Weekly", "Daily"), key = "freq_conf")

    # Pasos:
    # 1. Se agrupan los datos por fecha (Máximo global)
    # 2. Se convierten las fechas en strings a fechas
    global_confirmed = dataset[["confirmed", "date"]].groupby(by = ["date"]).max().reset_index()
    global_confirmed["date"] = pd.to_datetime(global_confirmed["date"])

    # Si los datos se desean mostrar de forma semanal
    if data_freq == "Weekly":
        global_confirmed = global_confirmed[global_confirmed["date"].dt.dayofweek == 0]

    # Si se desean presentar las diferencias entre datos
    # 1. Se calculan las diferencias
    # 2. Se elimina la última fila de las diferencias
    if sequence_type == "Difference":
        global_confirmed["confirmed"] = global_confirmed["confirmed"].diff().fillna(0)
        global_confirmed = global_confirmed.drop(global_confirmed.tail(1).index)
        global_confirmed["perc_change"] = global_confirmed["confirmed"].pct_change().replace([np.inf, -np.inf], np.nan).fillna(0) * 100

        figure_labels = {"date": "Date", "confirmed": "Confirmed Difference"}
        hover_data = {
            "% Change": (':.1f', global_confirmed["perc_change"])
        }
    else:
        figure_labels = {"date": "Date", "confirmed": "Confirmed Cases"}
        hover_data = {}

    # Creación de gráfica de plotly
    fig = px.bar(
        global_confirmed, 
        x ="date", 
        y ="confirmed",
        labels = figure_labels,
        hover_data = hover_data
    )
    fig.update_traces(marker_line_width = 0, marker_color = "#9066AD", selector=dict(type="bar"))
    col1.plotly_chart(fig, use_container_width = True)


# MUERTES
# ----------------
with st.container():
    col1, col2 = st.columns([4, 1])

    # Espacio vacío arriba de los controles
    col2.markdown("""
    #
    ### Controls
    """)

    # Controles
    sequence_type = col2.radio("Sequence Type", ("Cumulative", "Difference"), key = "seq_death")
    data_freq = col2.radio("Data Frequency", ("Weekly", "Daily"), key = "freq_death")

    # Se extraen los datos a graficar
    global_deaths = dataset[["deaths", "date"]].groupby(by = ["date"]).max().reset_index()
    global_deaths["date"] = pd.to_datetime(global_deaths["date"])

    # Si los datos se desean mostrar de forma semanal
    if data_freq == "Weekly":
        global_deaths = global_deaths[global_deaths["date"].dt.dayofweek == 0]

    # Si se desean presentar las diferencias entre datos
    # 1. Se calculan las diferencias
    # 2. Se elimina la última fila de las diferencias
    if sequence_type == "Difference":
        global_deaths["deaths"] = global_deaths["deaths"].diff().fillna(0)
        global_deaths = global_deaths.drop(global_deaths.tail(1).index)
        global_deaths["perc_change"] = global_deaths["deaths"].pct_change().replace([np.inf, -np.inf], np.nan).fillna(0) * 100
        
        figure_labels = {"date": "Date", "deaths": "Death Difference"}
        hover_data = {
            "% Change": (':.1f', global_deaths["perc_change"])
        }

    else:
        figure_labels = {"date": "Date", "deaths": "Deaths"}
        hover_data = {}

    # Creación de gráfica de plotly
    # Date=%{x}<br>Deaths=%{y}<extra></extra>
    fig = px.bar(
        global_deaths, 
        x ="date", 
        y="deaths",
        labels = figure_labels,
        hover_data = hover_data)
    fig.update_traces(marker_line_width = 0, marker_color = "#DF5941", selector=dict(type="bar"))
    col1.plotly_chart(fig, use_container_width = True)

# ----------------
# SITUACIÓN POR CONTINENTE
# ----------------
st.markdown("""
<div class = "subsection">
    <h2 class = "subsection-text">  Situation by Continent  </h2>
</div>
<hr>
""", unsafe_allow_html = True)

# Data agrupada por continente
continent_data = dataset[["confirmed", "deaths", "continent", "date", "population", "recovered"]].groupby(by = ["continent", "date"]).sum().reset_index()
continent_data = continent_data[continent_data["continent"] != "Unknown"]
continent_data["incidence"] = (continent_data['confirmed'] / continent_data['population']) * 100000

color_map = dict(zip(continent_data["continent"].unique(), px.colors.qualitative.Set1))

with st.container():

    # Columnas de control
    col1, col2, col3 = st.columns([1, 1, 1])

    # Obtención de valores para cada control
    metric = col1.selectbox('Metric', ('Confirmed Cases', 'Deaths', 'Incidence'), key = "metric_continent")
    data_freq = col2.selectbox('Data Frequency', ('Weekly', 'Daily'), key = "data_freq_continent")
    sequence_type = col3.selectbox('Sequence Type', ('Cumulative', 'Difference'), key = "sequence_type_continent")

    # CONTROL: Tipo de métrica a desplegar
    if metric == "Confirmed Cases":
        metric_type = "confirmed"
        metric_label = "Number of Confirmed Cases"
    elif metric == "Deaths":
        metric_type = "deaths"
        metric_label = "Deaths"
    elif metric == "Incidence":
        metric_type = "incidence"
        metric_label = "Cases per 100,000 people"

    # CONTROL: Muestreo de datos semanal
    # Se emplean todas las fechas que consistan de un lunes
    if data_freq == "Weekly":
        continent_data = continent_data[continent_data["date"].dt.dayofweek == 0]
    
    # CONTROL: Presentar las diferencias entre datos
    # 1. Se calculan las diferencias
    # 2. Se elimina la última fila de las diferencias
    # 3. Se agrega la columna de porcentaje de cambio
    if sequence_type == "Difference":
        continent_data[metric_type + "_diff"] = continent_data[metric_type].diff().fillna(0)
        continent_data = continent_data[continent_data["date"] != continent_data["date"].min()]
        continent_data["perc_change"] = continent_data[metric_type].pct_change().replace([np.inf, -np.inf], np.nan).fillna(0) * 100

        metric_label = metric_label + " (Difference)"
        hover_data = {
            "% Change": (':.1f', continent_data["perc_change"])
        }
    else:
        continent_data[metric_type + "_diff"] = continent_data[metric_type]
        hover_data = {}

    # Columnas de plots
    col1, col2 = st.columns([2, 3])

    # PLOT: Suma por continente
    fig = px.bar(
        continent_data[[metric_type, "continent"]]
            .groupby(by = "continent")
            .max()
            .reset_index()
            .sort_values(by = metric_type, ascending = False), 
        x = metric_type, 
        y = "continent", 
        color = "continent",
        orientation='h',
        text = metric_type,
        labels = {metric_type: metric_label.replace(" (Difference)", "")},
        color_discrete_map = color_map
    )
    fig.update_layout(yaxis_title = None)
    fig.update_traces(showlegend=False, texttemplate='%{text:.3s}')
    col1.plotly_chart(fig, use_container_width = True)

    # PLOT: Evolución temporal
    fig = px.bar(
        continent_data.sort_values(by = metric_type + "_diff", ascending = False), 
        x = "date", 
        y = metric_type + "_diff", 
        color = "continent",
        color_discrete_map = color_map,
        labels = {"date": "Date", metric_type + "_diff": metric_label, "continent": "Continent"},
        hover_data = hover_data
    )
    fig.update_traces(marker_line_width = 0, selector=dict(type="bar"))
    col2.plotly_chart(fig, use_container_width = True)

# ----------------
# SITUACIÓN POR PAÍS
# ----------------
st.markdown("""
<div class = "subsection">
    <h2 class = "subsection-text">  Situation by Country  </h2>
</div>
<hr>
""", unsafe_allow_html = True)

country_data = dataset[["confirmed", "deaths", "country_region", "date", "population", "code"]].groupby(by = ["country_region", "date", "code"]).sum().reset_index()

country_recovered = dataset[["country_region", "recovered"]].groupby(by = ["country_region"]).max().fillna(0).reset_index()

country_data = pd.merge(left = country_data, right = country_recovered, on = ["country_region"], how = "left")

top10 = country_data[country_data["date"] == latest_date].sort_values(by = "confirmed", ascending = False).head(10)

total_rates = (top10["confirmed"] / top10["population"]) * 100 + \
              (top10["deaths"] / top10["confirmed"]) * 100 + \
              (top10["recovered"] / top10["confirmed"]) * 10

st.markdown("""
### Comparison
Comparison of the infection rate, death rate and recovery rate of up to 10 countries. By default, the 10 countries with the largest number of confirmed cases are selected.
#
""")

with st.container():

    col1, col2 = st.columns([6, 1])

    options = col2.multiselect(
        'Countries to Compare', 
        country_data["country_region"].unique().tolist(), 
        top10["country_region"].unique().tolist()
    )

    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name = 'Infection Rate',
            x = (top10["confirmed"] / top10["population"]) * (100/total_rates),
            y = top10["country_region"],
            orientation = "h",
            marker=dict(
                color='#9066AD',
                line=dict(color='#654779', width=3)
            ),
            text = (top10["confirmed"] / top10["population"]) * 100,
            textposition = "inside",
            texttemplate = '%{text:.3s}%',
            insidetextanchor="middle"
        )
    )
    fig.add_trace(
        go.Bar(
            name = 'Fatality Rate',
            x = (top10["deaths"] / top10["confirmed"]) * (100/total_rates),
            y = top10["country_region"],
            orientation = "h",
            marker=dict(
                color='#DF5941',
                line=dict(color='#AC4432', width=3)
            ),
            text = (top10["deaths"] / top10["confirmed"]) * 100,
            textposition = "inside",
            texttemplate = '%{text:.3s}%',
            insidetextanchor="middle"
        )
    )
    fig.add_trace(
        go.Bar(
            name = 'Recovery Rate',
            x = (top10["recovered"] / top10["confirmed"]) * (10/total_rates),
            y = top10["country_region"],
            orientation = "h",
            marker=dict(
                color='#53B174',
                line=dict(color='#3B7D52', width=3)
            ),
            text = (top10["recovered"] / top10["confirmed"]) * 100,
            textposition = "inside",
            texttemplate = '%{text:.3s}%',
            insidetextanchor="middle"
        )
    )
    fig.update_layout(
        barmode = "stack",
        xaxis=dict(
            showgrid = False,
            showline = False,
            showticklabels = False,
            zeroline = False
        ),
        height = 700,
        plot_bgcolor='rgba(147,112,219,0)',
        font = dict(size=18),
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
    )
    fig.update_yaxes(ticksuffix = "      ")
    col1.plotly_chart(fig, use_container_width = True)

st.markdown("""
--------
### Individual Analysis
Statistics for an individual country
#
""")

with st.container():

    col1, col2, col3 = st.columns([1, 1, 1])

    # Obtenición de país a analizar
    selected_country = col1.selectbox('Country to Visualize', country_data["country_region"].unique().tolist())
    sequence_type = col2.selectbox("Sequence Type", ("Cumulative", "Difference"), key = "seq_type_country")
    sampling_freq = col3.selectbox("Sampling Frequency", ("Weekly", "Daily"), key = "sampl_freq_country")

    # Código ISO del país seleccionado
    selected_country_code = country_data.loc[country_data["country_region"] == selected_country, "code"].tolist()[0]

    # Datos de país seleccionado
    selected_country_data = dataset[dataset['country_region'] == selected_country]

    # CONTROL: Muestreo semanal
    if sampling_freq == "Weekly":
        selected_country_data = selected_country_data[selected_country_data["date"].dt.dayofweek == 0]
    
    # CONTROL: Datos diferenciales o acumulativos
    if sequence_type == "Difference":

        # Procesado de casos confirmados
        selected_country_data["confirmed"] = selected_country_data["confirmed"].diff().fillna(0)
        selected_country_data["conf_perc_change"] = selected_country_data["confirmed"].pct_change().replace([np.inf, -np.inf], np.nan).fillna(0) * 100

        # Procesado de muertes
        selected_country_data["deaths"] = selected_country_data["deaths"].diff().fillna(0)
        selected_country_data["death_perc_change"] = selected_country_data["deaths"].pct_change().replace([np.inf, -np.inf], np.nan).fillna(0) * 100

        # Se elimina la primera y última fecha del cambio
        earliest_date = selected_country_data["date"].min()
        latest_date = selected_country_data["date"].max()
        selected_country_data = selected_country_data[(selected_country_data["date"] != earliest_date) & (selected_country_data["date"] != latest_date)]

with st.container():

    col1, col2, col3, col4 = st.columns([0.5, 1, 0.5, 3])

    # API de banderas: https://flagpedia.net/download/api
    import requests
    response = requests.get(f"https://flagcdn.com/w320/{selected_country_code.lower()}.png")

    col2.markdown("""
    #
    # 
    #  
    """)

    # Se despliega la bandera del país seleccionado
    col2.image(response.content, caption = f"{selected_country}'s flag")

    col2.metric("Population", f"{selected_country_data['population'].max() / 1000000:.2f}M")
    col2.metric("Case-Fatality Ratio", f"{(selected_country_data['deaths'].max() / selected_country_data['confirmed'].max()) * 100:.1f}%")
    col2.metric("Incidence (Cases per 100k people)", f"{(selected_country_data['confirmed'].max() / selected_country_data['population'].max()) * 100000:.0f} cases")

    # Creación de gráfica de plotly
    fig = px.bar(
        selected_country_data, 
        x ="date", 
        y = "confirmed",
        labels = {"confirmed": "Confirmed Cases Difference", "date": "Date"} if (sequence_type == "Difference") else {"confirmed": "Confirmed Cases", "date": "Date"},
        hover_data = {"% Change": (':.1f%', selected_country_data["conf_perc_change"])} if (sequence_type == "Difference") else {}
    )
    fig.update_traces(marker_line_width = 0, marker_color = "#9066AD", selector=dict(type="bar"))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    col4.plotly_chart(fig, use_container_width = True)

    # Creación de gráfica de plotly
    fig = px.bar(
        selected_country_data, 
        x ="date", 
        y = "deaths",
        labels = {"deaths": "Death Differences", "date": "Date"} if (sequence_type == "Difference") else {"deaths": "Deaths", "date": "Date"},
        hover_data = {"% Change": (':.1f%', selected_country_data["death_perc_change"])} if (sequence_type == "Difference") else {}
    )
    fig.update_traces(marker_line_width = 0, marker_color = "#DF5941", selector=dict(type="bar"))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    col4.plotly_chart(fig, use_container_width = True)
