from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import XCom

from data_ingestion import ingest
from data_transformation import transform_into_csv
from train_model import compute_lr_score, compute_dt_score, compute_rf_score, save_best_model

############################### DAG Definition ########################################
my_dag=DAG(
    dag_id='airflow_exam',
    description='the exam validation solution',
    tags=['datascientest', 'exam'],
    schedule_interval= '* * * * *',
    default_args={
        'owner':'airflow', 
        'start_date': days_ago(0, minute=1)
    },
    catchup=False
)

################################ TASKS ##########################################

task_1= PythonOperator(
    task_id='retrieve_raw_data',
    dag=my_dag,
    python_callable=ingest,
    retries=5,
    retry_delay=timedelta(seconds = 15)
)

task_2 = PythonOperator(
    task_id='transform_into_data.csv',
    dag=my_dag,
    python_callable= transform_into_csv,
    op_kwargs={
        'n_files':20,
        'filename':'data.csv'
    }
)

task_3 = PythonOperator(
    task_id='transform_into_fulldata.csv',
    dag=my_dag,
    python_callable= transform_into_csv,
    op_kwargs={
        'n_files':None,
        'filename':'fulldata.csv'
    }
)

task_4 = PythonOperator(
    task_id='compute_lr_score',
    dag=my_dag,
    python_callable= compute_lr_score
)

task_5 = PythonOperator(
    task_id='compute_dt_score',
    dag=my_dag,
    python_callable= compute_dt_score
)

task_6 = PythonOperator(
    task_id='compute_rf_score',
    dag=my_dag,
    python_callable= compute_rf_score
)

task_7 = PythonOperator(
    task_id='train_best_model',
    dag=my_dag,
    python_callable= save_best_model
)

task_1 >> [task_2, task_3]
task_3 >> [task_4, task_5, task_6]
[task_4, task_5, task_6] >> task_7