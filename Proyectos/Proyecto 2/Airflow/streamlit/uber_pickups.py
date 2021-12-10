import streamlit as st
import pandas as pd
import numpy as np

"""
# Uber Pickups Exercise
"""

# ===============
# DESCARGA DATA
# ===============

DATA_URL = "https://s3-us-west-2.amazonaws.com/streamlit-demo-data/uber-raw-data-sep14.csv.gz"

# Función para descargar a cache el CSV descargado
@st.cache(allow_output_mutation=True)
def download_data():
    return pd.read_csv(DATA_URL)

# ===============
# SIDEBAR
# ===============

nrow = st.sidebar.slider("No. rows to display: ", 0, 10000, value= 1000)
hour_range = st.sidebar.slider("Select the hour range", 0, 24, value = (8, 17))

# Desplegar el rango de horas seleccionadas
st.sidebar.write("Hours selected: ", hour_range[0], hour_range[1])

# ===============
# MAPA
# ===============

# 1. Se descarga automáticamente el archivo y se guarda en un dataframe en caché
# 2. Se extraen solo algunas columnas
# 3. Se renombran todas las columnas
# 4. Se convierte la columna de "Date/Time" a datetime
# 5. Se ordena el dataframe según la fecha
data = (download_data()   
        .rename(columns={"Date/Time": "date_time", "Lat": "lat", "Lon": "lon", "Base": "base"})
        .assign(datetime = lambda df: pd.to_datetime(df["date_time"]))
        .loc[lambda df: (df.date_time.dt.hour >= hour_range[0]) & (df.date_time.dt.hour < hour_range[1])]
        .loc[1:nrow] 
        .sort_values(by=["date_time"]) 
        )

# Se despliega el dataframe
data

# Se muestra la data en la forma de un mapa
st.map(data)

# ===============
# BAR PLOT
# ===============

import altair as alt

# Se extraen las horas de cada columna
data["hours"] = data["date_time"].dt.hour

# Gráfica de barras de altair
fig = (
    alt.Chart(data)
    .mark_bar(size = 20)
    .encode(
        x=alt.X("hours", title="Hora de Viaje"),
        y=alt.Y('count()', title="Número de Viajes"),
        tooltip=[
            alt.Tooltip("hours", title="Hora", format=".0f")
        ],
    )
)

st.altair_chart(fig, use_container_width=False)

