import csv
import os
import pandas as pd
import lep_config

def select_zt_issues():
    folder = lep_config.folder
    zt_folder = os.path.join(folder, "zootaxa")
    file_latest = os.path.join(zt_folder, "issues_latest.csv")
    file_previous = os.path.join(zt_folder, "issues_previous.csv")
    file_new = os.path.join(zt_folder, "issues_new.csv")

    if os.path.exists(file_latest):

        if os.path.exists(file_previous):
            previous = pd.read_csv(file_previous, dtype=str, keep_default_na=False, sep=",")
        else:
            previous = None
        
        latest = pd.read_csv(file_latest, dtype=str, keep_default_na=False, sep=",")
        
        if previous is not None:
            new = latest[~latest.url.isin(previous.url)]
        else:
            new = latest          

        new.to_csv(file_new, index=False)

        if os.path.exists(file_previous):
            os.remove(file_previous)
        os.rename(file_latest, file_previous)
