import os

import coldp_sort
import pandas as pd
from coldp import COLDP

import gli_config as cfg


def summarise():
    if os.path.exists(cfg.coldp_path) and os.path.isdir(cfg.coldp_path):
        coldp = COLDP(cfg.scratch_folder, cfg.coldp_name, issues_to_stdout=True)
        hierarchy = coldp_sort.build_hierarchy(coldp)
        hierarchy = pd.merge(
            hierarchy[
                (hierarchy["genus"] != "")
                | (hierarchy["subgenus"] != "")
                | (hierarchy["species"] != "")
                | (hierarchy["subspecies"] != "")
            ].drop(columns=["scientificName", "rank"]),
            coldp.names.drop(columns=["genus", "status", "remarks", "code"]),
            left_on="nameID",
            right_on="ID",
            how="left",
        )
        hierarchy.to_csv(cfg.summary_file, index=False)
        coldp.references.to_csv(cfg.reference_file, index=False)
