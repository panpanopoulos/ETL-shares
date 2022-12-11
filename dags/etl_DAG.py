from datetime import datetime,timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from etl_process import run_etl

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2022, 11, 1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}
dag = DAG(
    'etl_DAG',
    default_args=default_args,
    description='etl DAG',
    schedule_interval='0 15 * * *',
)

run_xetra_etl = PythonOperator(
    task_id='run_etl_process',
    python_callable=run_etl,
    dag=dag,
)

run_xetra_etl