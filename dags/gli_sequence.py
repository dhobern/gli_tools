import os
from coldp import COLDP
import coldp_sort
import gli_config as cfg
import pandas as pd


def sequence():
    if os.path.exists(cfg.coldp_path) and os.path.isdir(cfg.coldp_path):
        coldp = COLDP(cfg.scratch_folder, cfg.coldp_name, issues_to_stdout=True)
        taxa = pd.merge(coldp.taxa, coldp.names[["ID", "scientificName"]], how="left", left_on="nameID", right_on="ID", suffixes=("", "_name"))
        taxa["ordinal"] = ""
        for i, name in enumerate(cfg.superfamilies, start=1):
            taxa.loc[taxa["scientificName"]==name, ["ordinal"]] = str(i)
        taxa.drop(["scientificName", "ID_name"], axis=1, inplace=True)
        coldp.taxa = taxa
        coldp.save()
