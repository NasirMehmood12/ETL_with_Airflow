import sys

sys.path.insert(0, "/opt/airflow")
sys.path.insert(0, "/opt/airflow/scripts")

from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

import sys
sys.path.insert(0, "/opt/airflow/scripts")

from extract import extract_data
from transform import transform_data
from load import load_data
from google_sheet import upload_to_google_sheets

with DAG(
    dag_id="cfpb_etl_pipeline",
    start_date=datetime(2026, 11, 13),
    schedule="@daily",
    catchup=False,
    tags=["CFPB", "ETL"],
) as dag:

    extract = PythonOperator(
        task_id="extract_data",
        python_callable=extract_data,
    )

    transform = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
    )

    load = PythonOperator(
        task_id="load_data",
        python_callable=load_data,
    )

    google_sheets = PythonOperator(
        task_id="upload_to_google_sheets",
        python_callable=upload_to_google_sheets,
    )

    extract >> transform >> load >> google_sheets
