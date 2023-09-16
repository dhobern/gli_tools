import os
from coldp import COLDP
import coldp_sort
import gli_config as cfg
import pandas as pd

def summarise():
    if os.path.exists(cfg.coldp_path) and os.path.isdir(cfg.coldp_path):
        coldp = COLDP(cfg.scratch_folder, cfg.coldp_name, issues_to_stdout=True)
        hierarchy = coldp_sort.build_hierarchy(coldp)
        hierarchy = pd.merge(
            hierarchy.drop(columns=["scientificName", "rank"]),
            coldp.names.drop(
                columns=["genus", "status", "remarks", "code", "link"]
            ),
            left_on="nameID",
            right_on="ID",
            how="left",
        )
        hierarchy.to_csv(cfg.summary_file, index=False)
        coldp.references.to_csv(cfg.reference_file, index=False)
