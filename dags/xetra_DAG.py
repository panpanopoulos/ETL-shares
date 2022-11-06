from datetime import datetime,timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from xetra_etl import run_etl

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
    'xetra_DAG',
    default_args=default_args,
    description='xetra DAG',
    schedule_interval='0 15 * * *',
)

run_xetra_etl = PythonOperator(
    task_id='run_xetra_etl',
    python_callable=run_etl,
    dag=dag,
)

run_xetra_etl