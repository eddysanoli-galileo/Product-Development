import streamlit as st
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from streamlit_folium import folium_static
from functions import process_folium_map_data
import datetime

# Layout ancho (Similar a una página web tradicional)
st.set_page_config(layout="wide")

# ================
# TITULO
# ================

st.title('COVID-19 Dashboard')

# ================
# DATASET
# ================

try: 
    # Conexión con base de datos
    # Argumento: 'mysql+mysqlconnector://[user]:[pass]@[host]:[port]/[schema]'
    engine = create_engine('mysql+mysqlconnector://test:test123@db:3306/test')

    # Se extrae todo el dataset
    dataset = pd.read_sql(
        "SELECT * FROM covid_data",
        con = engine
    )

except Exception as e:
    st.write("Database not yet available.")
    st.image("streamlit/map.PNG")

# ===============
# SIDE BAR
# ===============

st.sidebar.markdown("""
# Options
## Map Date
""")

analysis_date = st.sidebar.date_input(
    'Date for COVID data', 
    value = dataset['date'].max(),
    min_value = dataset['date'].min(),
    max_value = dataset['date'].max()
)

st.sidebar.markdown(f"""
##### Dataset date range: { dataset['date'].min().date().strftime('%m/%d/%Y') } - { dataset['date'].max().date().strftime('%m/%d/%Y') }
""")

# ================
# FOLIUM MAP
# ================

# Solo se renderiza el mapa si el dataset no está vacío
if not dataset.empty:
    #with st.spinner("Loading Map..."):
    #   map = process_folium_map_data(dataset, analysis_date)
    #   folium_static(map, width = 1420, height = 580)
    st.image("streamlit/map.PNG")

# ================
# CONTENT
# ================

st.title("Global Situation")

with st.container():
    col1, col2 = st.columns([4, 1])
    col1.bar_chart(dataset[["confirmed", "date"]])
    col2.write("Controles")

with st.container():
    col1, col2 = st.columns([4, 1])
    col1.bar_chart(np.random.randn(50, 3))
    col2.write("Controles")

"""
## Show me some graphs
"""

# Se generan 20 muestras para 3 columnas diferentes
df_to_plot = pd.DataFrame(
    np.random.randn(20, 3), columns=["Column A", "Column B", "Column C"]
)

st.line_chart(df_to_plot)

"""
## Let's plot a map!
"""

# Se le deben de colocar nombres a las columnas o Streamlit retorna un error
df_lat_lon = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns = ["lat", "lon"]
)

st.map(df_lat_lon)

if st.checkbox("Show DataFrame"):
    df_lat_lon

"""
## Let's Try Some Widgets!

### 1. Slider
"""

# Min value: Valor mínimo
# Max value: Valor máximo
# Value: Valor predeterminado
x = st.slider("Select a Value for X", min_value=1, max_value=100, value=4)
y = st.slider("Select a power for X", min_value=0, max_value=5, value=2)
st.write(x, " power", y, " = ", x**y)

"""
### 2. What about Options?
"""

def test():
    st.write("Función ejecutada :)")

option_list = range(1,10)
option = st.selectbox("Which number do you like best?", option_list, on_change=test)
st.write("Your favorite number is: ", option)


"""
### 3. How About a Progress Bar?
"""

import time

label = st.empty()
progress_bar = st.progress(0)

# Se ejecuta luego de haber finalizado la barra de progreso de arriba
"The wait is done"


