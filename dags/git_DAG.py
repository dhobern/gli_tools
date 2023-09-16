from airflow import DAG
from airflow.operators.bash import BashOperator
import datetime
import pendulum

local_tz = pendulum.timezone("Australia/Canberra")

dag = DAG(
    dag_id="git_updates",
    start_date=datetime.datetime(2023, 8, 10, tzinfo=local_tz),
    schedule_interval="0 0 * * *",
    default_args={"email": ["dhobern@gmail.com"], "email_on_failure": True},
    catchup=False,
)

zip = BashOperator(
    task_id="pull",
    bash_command="cd /home/dhobern/gli_tools && git fetch && git pull && cp dags/*.py /home/dhobern/airflow/dags",
    dag=dag,
)
