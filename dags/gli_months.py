import os
import pandas as pd
import gli_config as cfg

def report_months():
    if os.path.exists(cfg.summary_file):
        summary = pd.read_csv(cfg.summary_file, dtype=str, keep_default_na=False, sep=",")
        summary["year"] = summary["modified"].str[0:4]
        summary["month"] = summary["modified"].str[5:7]
        summary.loc[summary["superfamily"]=="",["superfamily", "family", "subfamily", "tribe"]] = "Lepidoptera"
        pivot = pd.pivot_table(summary, values='scientificName', index=['year', 'month', 'superfamily', 'family', 'subfamily', 'tribe'],
                                aggfunc=pd.Series.nunique)
        pivot.to_csv(cfg.month_file, index=True)
