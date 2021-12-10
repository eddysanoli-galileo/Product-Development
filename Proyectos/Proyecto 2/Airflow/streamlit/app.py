import streamlit as st
import numpy as np
import pandas as pd

st.title('Amo a mi amorcito ❤️')

"""
## Potencialidades

- Es hermosa
- Es perfecta
- Canta precioso
- Da los mejores abrazos, besos, consejos y apapachos
- Wifey 100%
- Corazón enorme y de oro
- La mejor amiga
- La mejor confidente
- Es un pato 🦆
"""

x = 4
st.write(x, " square is ", x*x)

# Sintáxis equivalente pero menos ordenada
x = 4
x, "square is ", x*x

# Dataframes
st.write("This is a DataFrame exampe")
st.write(pd.DataFrame({
    'Column A': ["A", "B", "C", "D"],
    "Column B": [1, 2, 3, 4]
}))

"""
# Title: This is a Title Tag
This is another example for data frames
"""

# Dataframes
st.write("This is a DataFrame exampe")
st.write(pd.DataFrame({
    'Column A': ["A", "B", "C", "D"],
    "Column B": [1, 2, 3, 4]
}))

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

# ===============
# SIDE BAR
# ===============

st.sidebar.write("This is a sidebar")
option_side = st.sidebar.selectbox("Select a Side Number", option_list)
st.sidebar.write("The selection is: ", option_side)

st.sidebar.write("Another slider")
another_slider = st.sidebar.slider("Select Range", min_value=0.0, max_value=100.0, value=(25.0, 75.0))

st.sidebar.write("The range selected is: ", another_slider)


