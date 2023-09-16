import os
from zipfile import ZipFile
import shutil
import gli_config as cfg
from airflow.hooks.base_hook import BaseHook

def upload_coldp():
    if os.path.exists(cfg.coldp_file):
        credentials = BaseHook.get_connection("clb_gli")
        os.system(f"curl -s --user {credentials.login}:{credentials.password} -H 'Content-Type: application/zip' --data-binary @{cfg.coldp_file} -X POST '{credentials.host}'")