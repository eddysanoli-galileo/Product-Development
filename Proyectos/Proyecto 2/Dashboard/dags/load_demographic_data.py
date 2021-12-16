import os
import pandas as pd
import numpy as np
import pycountry_convert as pc

from airflow import DAG
from airflow.contrib.hooks.fs_hook import FSHook
from airflow.contrib.sensors.file_sensor import FileSensor
from airflow.hooks.mysql_hook import MySqlHook
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from structlog import get_logger

logger = get_logger()

# ===============
# DECLARACIÓN DE DAG
# ===============

dag = DAG('load_demographic_data', description = "DAG for loading demographic data to the database (per country)",
          default_args = {
              'owner': 'eddysanoli',
              'depends_on_past': False,
              'max_active_runs': 1,
              'start_date': days_ago(2)
          },
          is_paused_upon_creation=False,
          schedule_interval = "0 1 * * *",
          catchup = False)

# ===============
# FUNCIONES
# ===============

# --------------
# FUNCIÓN: Obtener continente y código de cada país
def get_country_continentAndCode(**context):

    confirmed = pd.read_csv(f"{FSHook('fs_default').get_path()}/time_series_covid19_confirmed_global.csv")
    
    # Lista de paises únicos en dataset de COVID
    countries = confirmed["Country/Region"].unique().tolist()

    # Listas vacías de continentes y códigos de país
    continents = []
    country_codes = []

    # Para cada país en la lista encontrada
    for country in countries:

        # Se mapean los nombres de paises de los datos de COVID a los nombres
        # de país utilizados en PyCountry (En caso no sean iguales).
        map2pycountry = {
            "US": "United States of America", 
            "Korea, South": "South Korea",
            "Burma": "Myanmar",
            "Taiwan*": "Taiwan",
            "West Bank and Gaza": "Palestine",
            "Congo (Kinshasa)": "Democratic Republic of the Congo",
            "Cote d'Ivoire": "Ivory Coast"
        }

        if country in map2pycountry.keys():
            country = map2pycountry[country]

        # Se obtiene el nombre de continente obteniendo el código de cada país,
        # luego utilizando ese código para obtener el código de continente y finalmente
        # traduciendo el código de continente a un nombre. En caso no se encuentre un match
        # se coloca el código y continente como "Unknown"
        try: 
            country_code = pc.country_name_to_country_alpha2(country, cn_name_format="default")
            continent_code = pc.country_alpha2_to_continent_code(country_code)

            continent_code2name = {
                "AF" : "Africa", 
                "NA" : "North America", 
                "OC" : "Oceania", 
                "AN" : "Antarctica", 
                "AS" : "Asia", 
                "EU" : "Europe", 
                "SA" : "South America"
            }

            continents.append(continent_code2name[continent_code])
            country_codes.append(country_code)

        except Exception as e:
            continents.append("Unknown")
            country_codes.append("UNKNOWN")

    # Dataframe con el código, nombre y continente de cada país
    df_country = pd.DataFrame({"Country Code": country_codes, "Country": countries, "Continent": continents})

    # Corrección manual de algunos continentes
    manual_correction_continents = {
        "Congo (Brazzaville)": "Africa",
        "Timor-Leste": "Asia",
        "Kosovo": "Europe",
        "Holy See": "Europe",
        "Guatemala": "Central America",
        "El Salvador": "Central America",
        "Nicaragua": "Central America",
        "Honduras": "Central America",
        "Costa Rica": "Central America",
        "Belize": "Central America",
        "Panama": "Central America",
        "Summer Olympics 2020": "Asia"
    }

    for key in manual_correction_continents.keys():
        df_country.loc[df_country["Country"] == key, "Continent"] = manual_correction_continents[key]

    # Corrección manual de códigos
    manual_correction_codes = {
        "Congo (Brazzaville)": "COG",
        "Timor-Leste": "TLS",
        "Kosovo": "RKS",
        "Holy See": "VA"
    }

    for key in manual_correction_codes.keys():
        df_country.loc[df_country["Country"] == key, "Country Code"] = manual_correction_codes[key]

    ti = context['ti']
    ti.xcom_push(key = "country_data", value = df_country)
    

# --------------
# FUNCIÓN: Formatear los datos de población
def format_population(**context):

    df_population = pd.read_csv(f"{FSHook('fs_default').get_path()}/world_bank_population.csv")

    # Corrección de nombres de país en base de datos de población, para que
    # coincida con los nombres de país de los datos de COVID
    name_correction_population = {
        "Russian Federation": "Russia",
        "United States": "US",
        "Iran, Islamic Rep.": "Iran",
        "Taiwan*": "Taiwan",
        "Bahamas, The": "Bahamas",
        "Brunei Darussalam": "Brunei",
        "Myanmar": "Burma",
        "Czech Republic" : "Czechia",
        "Egypt, Arab Rep.": "Egypt",
        "Congo, Rep.": "Congo (Brazzaville)",
        "Congo, Dem. Rep.": "Congo (Kinshasa)",
        "Gambia, The": "Gambia",
        "Lao PDR": "Laos",
        "Micronesia, Fed. Sts.": "Micronesia",
        "Venezuela, RB" : "Venezuela",
        "Yemen, Rep.": "Yemen",
        "Slovak Republic": "Slovakia",
        "St. Vincent and the Grenadines": "Saint Vincent and the Grenadines",
        "Kyrgyz Republic": "Kyrgyzstan",
        "Syrian Arab Republic": "Syria",
        "St. Lucia": "Saint Lucia",
        "St. Kitts and Nevis": "Saint Kitts and Nevis",
        "Korea, Rep.": "Korea, South"
    }

    for key in name_correction_population.keys():   
        df_population.loc[df_population["Country Name"] == key, "Country Name"] = name_correction_population[key]

    ti = context['ti']
    ti.xcom_push(key = "population_data", value = df_population)

# --------------
# FUNCIÓN: Combinar datos de población y de país
def merge_data(**context):

    # Se obtiene la "ti" o "Task instance"
    ti = context['ti']

    # Se recuperan los datos de XCOM
    df_country = ti.xcom_pull(key = "country_data", task_ids = "get_country_continentAndCode")
    df_population = ti.xcom_pull(key = "population_data", task_ids = "format_population")

    # Año para el que se extraerá la población
    pop_year = "2020"

    # Se combinan los dos dataframes
    df_demography = pd.merge(
        left = df_country, 
        right = df_population[["Country Name", pop_year]], 
        left_on = "Country", 
        right_on = "Country Name", 
        how = "left"
    )

    # Se reemplazan los NANs con ceros los dataframes combinados
    df_demography[df_demography[pop_year].isna()] = df_demography[df_demography[pop_year].isna()].fillna(0)

    # Se renombra la columna de año y se elimina la redundante de nombre
    df_demography = df_demography.rename(columns = {pop_year: "Population"})
    df_demography = df_demography.drop(columns = ["Country Name"])

    # Se mueven los datos combinados a XCOM
    ti.xcom_push(key = "demography_data", value = df_demography)

# --------------
# FUNCIÓN: Se colocan los datos demográficos en la base de datos
def post_to_db(**context):

    # Se obtiene la "ti" o "Task instance"
    ti = context['ti']

    # Se recuperan los datos de XCOM
    df_demography = ti.xcom_pull(key = "demography_data", task_ids = "merge_data")

    # Se renombran las columnas del dataframe para ser congruente con
    # la tabla en base de datos
    df_demography = df_demography.rename(columns = {
        "Country Code": "code",
        "Country": "name",
        "Continent": "continent",
        "Population": "population"
    })

    # Para ejecutarlo de forma transaccional
    # (Editar la conexión en 'Connections' antes: Host = db / Schema = test / Login = test / Password = test123 / Port = 3306)
    connection = MySqlHook('mysql_default').get_sqlalchemy_engine()

    # Se agregan los datos a la base de datos
    # (Borrando los mismos primero)
    with connection.begin() as transaction:
        transaction.execute("DELETE FROM test.country_data WHERE 1=1")
        df_demography.to_sql('country_data', con = transaction, schema = 'test', if_exists = 'append', index = False)

    # Print a log
    logger.info(f"Rows Inserted: {len(df_demography.index)}")

# ===============
# SENSORES
# ===============

sensor_confirmed = FileSensor(task_id = 'confirmed_sensor',
                              dag = dag,
                              fs_conn_id = 'fs_default',
                              filepath = 'time_series_covid19_confirmed_global.csv',
                              poke_interval = 5,
                              timeout = 60)

sensor_population = FileSensor(task_id = 'population_sensor',
                               dag = dag,
                               fs_conn_id = 'fs_default',
                               filepath = 'world_bank_population.csv',
                               poke_interval = 5,
                               timeout = 60)

# ===============
# OPERADORES
# ===============

DAG_get_country_continentAndCode = PythonOperator(task_id = 'get_country_continentAndCode', dag = dag, python_callable = get_country_continentAndCode, provide_context=True)
DAG_format_population = PythonOperator(task_id = 'format_population', dag = dag, python_callable = format_population, provide_context=True)
DAG_merge_data = PythonOperator(task_id = 'merge_data', dag = dag, python_callable = merge_data, provide_context=True)
DAG_post_to_db = PythonOperator(task_id = 'post_to_db', dag = dag, python_callable = post_to_db, provide_context=True)

# ===============
# PIPELINE
# ===============

[sensor_population >> DAG_format_population,
 sensor_confirmed  >> DAG_get_country_continentAndCode] >> DAG_merge_data >> DAG_post_to_db