import os
import pandas as pd
import numpy as np
import gli_config

def report_families():
    folder = gli_config.folder
    for f in os.listdir(folder):
        if f.endswith("_summary.csv"):
            summary_path = os.path.join(folder, f)
            report_path = summary_path.replace("_summary.csv", "_families.csv")
            summary = pd.read_csv(summary_path, dtype=str, keep_default_na=False, sep=",")
            summary["year"] = summary["modified"].str[0:4]
            summary["month"] = summary["modified"].str[5:7]
            summary.loc[summary["superfamily"]=="",["superfamily", "family", "subfamily", "tribe"]] = "Lepidoptera"
            pivot = pd.pivot_table(summary, values='scientificName', index=['superfamily', 'family', 'subfamily', 'tribe', 'year', 'month'],
                                    aggfunc=pd.Series.nunique)
            pivot.to_csv(report_path, index=True)
