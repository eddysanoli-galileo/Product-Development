import pandas as pd
from airflow import DAG
from airflow.contrib.hooks.fs_hook import FSHook
from airflow.contrib.sensors.file_sensor import FileSensor
from airflow.hooks.mysql_hook import MySqlHook
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from structlog import get_logger
import os

dag = DAG('new_sales_dag', description = "This is a new implementation of the sales DAG",
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

COLUMNS = {
    "ORDERNUMBER": "order_number",
    "QUANTITYORDERED": "quantity_ordered",
    "PRICEEACH": "price_each",
    "ORDERLINENUMBER": "order_line_number",
    "SALES": "sales",
    "ORDERDATE": "order_date",
    "STATUS": "status",
    "QTR_ID": "qtr_id",
    "MONTH_ID": "month_id",
    "YEAR_ID": "year_id",
    "PRODUCTLINE": "product_line",
    "MSRP": "msrp",
    "PRODUCTCODE": "product_code",
    "CUSTOMERNAME": "customer_name",
    "PHONE": "phone",
    "ADDRESSLINE1": "address_line_1",
    "ADDRESSLINE2": "address_line_2",
    "CITY": "city",
    "STATE": "state",
    "POSTALCODE": "postal_code",
    "COUNTRY": "country",
    "TERRITORY": "territory",
    "CONTACTLASTNAME": "contact_last_name",
    "CONTACTFIRSTNAME": "contact_first_name",
    "DEALSIZE": "deal_size"}

DATE_COLUMNS = ["ORDERDATE"]

logger = get_logger()

def process_file():

    file_path = f"{FSHook('fs_default').get_path()}/sales.csv"
    df = (pd.read_csv(file_path, encoding = "ISO-8859-1", parse_dates = DATE_COLUMNS)
            .rename(columns = COLUMNS) 
         )

    # Para ejecutarlo de forma transaccional
    connection = MySqlHook('mysql_default').get_sqlalchemy_engine()

    # Se agregan los datos a la base de datos
    # (Borrando los mismos primero)
    with connection.begin() as transaction:
        transaction.execute("DELETE FROM test.sales WHERE 1=1")
        df.to_sql('sales', con = transaction, schema = 'test', if_exists = 'append', index = False)

    # Logger
    logger.info(f"Rows inserted {len(df.index)}")
    os.remove(file_path)
    logger.info(f'File {file_path} was deleted.')

    print(df)

# ===============
# SENSORES
# ===============

sensor = FileSensor(task_id = 'sales_sensor_file',
                    dag = dag,
                    fs_conn_id = 'fs_default',
                    filepath = 'sales.csv',
                    poke_interval = 5,
                    timeout = 60)

# ===============
# OPERADORES
# ===============

process_file_operator = PythonOperator(task_id = 'process_file',
                                       dag = dag,
                                       python_callable = process_file)

# ===============
# PIPELINE
# ===============

sensor >> process_file_operator
