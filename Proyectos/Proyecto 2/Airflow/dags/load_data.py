import os
import pandas as pd
import numpy as np

from airflow import DAG
from airflow.contrib.hooks.fs_hook import FSHook
from airflow.contrib.sensors.file_sensor import FileSensor
from airflow.hooks.mysql_hook import MySqlHook
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from structlog import get_logger

# ===============
# DECLARACIÓN DE DAG
# ===============

dag = DAG('load_data', description = "DAG for loading new COVID-19 data to the database",
          default_args = {
              'owner': 'eddysanoli',
              'depends_on_past': False,
              'max_active_runs': 1,
              'start_date': days_ago(2)
          },
          schedule_interval = "0 1 * * *",
          catchup = False)

# ===============
# FUNCIONES
# ===============

# FUNCIÓN: Convierte la data al formato de la base de datos
def to_database_format(data, column_name):

    # Dataset sin datos por fecha
    data_noFechas = data.iloc[:, 0:4]

    # Fechas cubiertas por la data
    fechas = data.iloc[:, 4:].columns.values

    # Número de fechas y número de combinaciones únicas de país y estado
    num_fechas = len(fechas)
    num_regiones = len(data)

    # Se repiten las regiones tantas veces como hay fechas
    # (Para que cada país tenga todas las fechas)
    df_out = data_noFechas.loc[np.repeat(data.index.values, num_fechas)]
    df_out = df_out.reset_index()

    # Se repite la secuencia de fechas tantas veces como hay regiones
    # (Se elimina la columna de index creada previamente por "reset_index")
    df_out["Date"] = pd.DataFrame(list(fechas) * num_regiones)
    df_out = df_out.drop(columns = ["index"])

    # Se extraen los casos confirmados y se ordenan para que coincidan con el orden
    # del resto de la tabla.
    df_out[column_name] = np.reshape(data.iloc[:, 4:].values, (-1, 1))

    return(df_out)


# --------------
# FUNCIÓN: Conversión de datos de confirmados
def format_confirmed(**context):

    confirmed = pd.read_csv(f"{FSHook('fs_default').get_path()}/time_series_covid19_confirmed_global.csv")
    db_confirmed = to_database_format(confirmed, "Confirmed")

    ti = context['ti']
    ti.xcom_push(key = "confirmed_data", value = db_confirmed)


# --------------
# FUNCIÓN: Conversión de datos de muertes
def format_deaths(**context):

    deaths = pd.read_csv(f"{FSHook('fs_default').get_path()}/time_series_covid19_deaths_global.csv")
    db_deaths = to_database_format(deaths, "Deaths")

    ti = context['ti']
    ti.xcom_push(key = "deaths_data", value = db_deaths)


# --------------
# FUNCIÓN: Conversión de datos de recuperados
def format_recovered(**context):

    recovered = pd.read_csv(f"{FSHook('fs_default').get_path()}/time_series_covid19_recovered_global.csv")
    db_recovered = to_database_format(recovered, "Recovered")

    ti = context['ti']
    ti.xcom_push(key = "recovered_data", value = db_recovered)


# --------------
# FUNCIÓN: Unir los dataframes de confirmados, recuperados y muertos
def merge_data(**context):

    # Se obtiene la "ti" o "Task instance"
    ti = context['ti']

    # Se recuperan los datos de XCOM
    db_confirmed = ti.xcom_pull(key = "confirmed_data", task_ids = "format_confirmed")
    db_deaths = ti.xcom_pull(key = "deaths_data", task_ids = "format_deaths")
    db_recovered = ti.xcom_pull(key = "recovered_data", task_ids = "format_recovered")

    # Unión de confirmados y muertes
    df_merge1 = pd.merge(left = db_confirmed, right = db_deaths, on = ["Province/State", "Country/Region", "Lat", "Long", "Date"])

    # Unión de confirmados, muertes y recuperados
    df_merge2 = pd.merge(left = df_merge1, right = db_recovered, on = ["Province/State", "Country/Region", "Lat", "Long", "Date"])

    ti.xcom_push(key = "merged_df", value = df_merge2)


# --------------
# FUNCIÓN: Postear a base de datos
def post_to_db(**context):

    ti = context['ti']
    merged_df = ti.xcom_pull(key = "merged_df", task_ids = "merge_data")
    
    print(merged_df)

# ===============
# SENSORES
# ===============

sensor_confirmed = FileSensor(task_id = 'confirmed_sensor',
                              dag = dag,
                              fs_conn_id = 'fs_default',
                              filepath = 'time_series_covid19_confirmed_global.csv',
                              poke_interval = 5,
                              timeout = 60)

sensor_deaths = FileSensor(task_id = 'deaths_sensor',
                           dag = dag,
                           fs_conn_id = 'fs_default',
                           filepath = 'time_series_covid19_deaths_global.csv',
                           poke_interval = 5,
                           timeout = 60)

sensor_recovered = FileSensor(task_id = 'recovered_sensor',
                              dag = dag,
                              fs_conn_id = 'fs_default',
                              filepath = 'time_series_covid19_recovered_global.csv',
                              poke_interval = 5,
                              timeout = 60)

# ===============
# OPERADORES
# ===============

DAG_format_confirmed = PythonOperator(task_id = 'format_confirmed', dag = dag, python_callable = format_confirmed, provide_context=True)
DAG_format_deaths = PythonOperator(task_id = 'format_deaths', dag = dag, python_callable = format_deaths, provide_context=True)
DAG_format_recovered = PythonOperator(task_id = 'format_recovered', dag = dag, python_callable = format_recovered, provide_context=True)
DAG_merge_data = PythonOperator(task_id = 'merge_data', dag = dag, python_callable = merge_data, provide_context=True)
DAG_post_to_db = PythonOperator(task_id = 'post_to_db', dag = dag, python_callable = post_to_db, provide_context=True)

# ===============
# PIPELINE
# ===============

[sensor_confirmed >> DAG_format_confirmed, 
 sensor_deaths    >> DAG_format_deaths, 
 sensor_recovered >> DAG_format_recovered] >> DAG_merge_data >> DAG_post_to_db