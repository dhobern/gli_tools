from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.sensors.filesystem import FileSensor
import datetime
import pendulum

import gli_unpack
import gli_summarise
import gli_sequence
import gli_months
import gli_citations
import gli_metrics
import gli_metadata
import gli_upload

local_tz = pendulum.timezone("Australia/Canberra")

dag = DAG(
    dag_id="gli_updates",
    start_date=datetime.datetime(2023, 8, 10, tzinfo=local_tz),
    schedule_interval="0 1,9,17 * * *",
    default_args={"email": ["dhobern@gmail.com"], "email_on_failure": True},
    catchup=False,
)

download = BranchPythonOperator(
    task_id="download",
    python_callable=gli_download.download_archive,
    dag=dag,
)

unpack = BranchPythonOperator(
    task_id="unpack",
    python_callable=gli_unpack.unpack_archive,
    dag=dag,
)

summarise = PythonOperator(
    task_id="summarise",
    python_callable=gli_summarise.summarise,
    dag=dag,
)

months = PythonOperator(
    task_id="months",
    python_callable=gli_months.report_months,
    dag=dag,
)

citations = PythonOperator(
    task_id="citations",
    python_callable=gli_citations.report_citations,
    dag=dag,
)

metrics = PythonOperator(
    task_id="metrics",
    python_callable=gli_metrics.report_metrics,
    dag=dag,
)

sequence = PythonOperator(
    task_id="sequence",
    python_callable=gli_sequence.sequence,
    dag=dag,
)

metadata = PythonOperator(
    task_id="metadata",
    python_callable=gli_metadata.update_metadata,
    dag=dag,
)

zip = BashOperator(
    task_id="zip",
    bash_command="cd /home/dhobern/airflow/scratch/gli_updates/gli && rm -f ../gli.zip && zip -r ../gli.zip *.csv *.yaml",
    dag=dag,
)

upload = PythonOperator(
    task_id="upload",
    python_callable=gli_upload.upload_coldp,
    dag=dag,
)

backup = BashOperator(
    task_id="backup",
    bash_command="rm -fr /home/dhobern/gli_backup/*; mv /home/dhobern/airflow/scratch/gli_updates/* /home/dhobern/gli_backup/",
    dag=dag,
)

cleanup = BashOperator(
    task_id="cleanup",
    bash_command="rm -fr /home/dhobern/airflow/scratch/gli_updates/*",
    dag=dag,
)

finish = EmptyOperator(
    task_id="finish",
    dag=dag,
)

download >> unpack >> summarise >> months
summarise >> citations
summarise >> metrics
summarise >> sequence
download >> finish
unpack >> finish
[months, citations, metrics] >> metadata
[metadata, sequence] >> zip >> upload >> backup >> cleanup >> finish
