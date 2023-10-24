import datetime

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

local_tz = pendulum.timezone("Australia/Canberra")

dag = DAG(
    dag_id="git_updates",
    start_date=datetime.datetime(2023, 8, 10, tzinfo=local_tz),
    schedule_interval="0 0 * * *",
    default_args={"email": ["dhobern@gmail.com"], "email_on_failure": True},
    catchup=False,
)

gli_pull = BashOperator(
    task_id="gli_pull",
    bash_command="cd /home/dhobern/git/gli_tools && git fetch && git pull && cp dags/*.py /home/dhobern/airflow/dags",
    dag=dag,
)

coldp_pull = BashOperator(
    task_id="coldp_pull",
    bash_command="cd /home/dhobern/git/py-coldp && git fetch && git pull && cp coldp*.py /home/dhobern/airflow/dags",
    dag=dag,
)

gli_pull >> coldp_pull
