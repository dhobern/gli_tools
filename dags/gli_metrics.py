import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
import re
import gli_config as cfg


def report_metrics():
    if os.path.exists(cfg.summary_file):
        summary = pd.read_csv(
            cfg.summary_file, dtype=str, keep_default_na=False, sep=","
        )
        summary["accepted"] = summary["status"].apply(
            lambda x: 1 if x == "accepted" else 0
        )
        summary["year"] = summary["authorship"].apply(
            lambda x: re.sub(r"[^0-9]*([1-2][0-9]{3})?.*", r"\1", str(x))
        )
        summary["year"] = summary["year"].apply(lambda x: np.nan if x == "" else int(x))
        summary["recent"] = summary["year"].apply(lambda x: 1 if x > 1985 else 0)
        summary["hasCitation"] = 0
        summary.loc[summary["referenceID"] != "", "hasCitation"] = 1
        import_date = "2017-08-01"
        one_year_ago = (datetime.today() - relativedelta(years=1)).strftime("%Y-%m-%d")
        if "modified" in summary.columns:
            summary["modifiedSinceImport"] = summary["modified"].apply(
                lambda x: 1 if x[0:10] > import_date else 0
            )
            summary["modifiedThisYear"] = summary["modified"].apply(
                lambda x: 1 if x[0:10] > one_year_ago else 0
            )
        ranks_of_interest = ["order", "superfamily", "family", "subfamily", "tribe"]
        ranks_for_index = []
        metrics_files = {
            "order": cfg.order_file,
            "superfamily": cfg.superfamily_file,
            "family": cfg.family_file,
            "subfamily": cfg.subfamily_file,
            "tribe": cfg.tribe_file,
        }
        for r in ranks_of_interest:
            print(f"Processing {r}")
            ranks_for_index.append(r)
            rank_pivot = pd.pivot_table(
                summary,
                values="scientificName",
                index=ranks_for_index,
                aggfunc=pd.Series.nunique,
            )
            rank_pivot.rename(columns={"scientificName": "nameCount"}, inplace=True)
            pivot = pd.pivot_table(
                summary[(summary["rank"] == "species") & (summary["accepted"] == 1)],
                values="scientificName",
                index=ranks_for_index,
                aggfunc=pd.Series.nunique,
            )
            pivot.rename(columns={"scientificName": "speciesCount"}, inplace=True)
            rank_pivot = pd.merge(rank_pivot, pivot, on=ranks_for_index)
            pivot = pd.pivot_table(
                summary, values="year", index=ranks_for_index, aggfunc="mean"
            )
            rank_pivot = pd.merge(rank_pivot, pivot, on=ranks_for_index)
            pivot = pd.pivot_table(
                summary, values="accepted", index=ranks_for_index, aggfunc="sum"
            )
            rank_pivot = pd.merge(rank_pivot, pivot, on=ranks_for_index)
            pivot = pd.pivot_table(
                summary, values="recent", index=ranks_for_index, aggfunc="sum"
            )
            rank_pivot = pd.merge(rank_pivot, pivot, on=ranks_for_index)
            pivot = pd.pivot_table(
                summary, values="hasCitation", index=ranks_for_index, aggfunc="sum"
            )
            rank_pivot = pd.merge(rank_pivot, pivot, on=ranks_for_index)
            rank_pivot["fractionSynonyms"] = (
                rank_pivot["nameCount"] - rank_pivot["accepted"]
            ) / rank_pivot["nameCount"]
            rank_pivot["fractionRecent"] = (
                rank_pivot["recent"] / rank_pivot["nameCount"]
            )
            rank_pivot["fractionHasCitation"] = (
                rank_pivot["hasCitation"] / rank_pivot["nameCount"]
            )
            this_year = datetime.today().year
            rank_pivot["metric"] = (
                (rank_pivot["year"] - 1758) / (this_year - 1758)
            ) * (
                1
                - (1 - rank_pivot["fractionSynonyms"])
                * (1 - rank_pivot["fractionRecent"])
                * (1 - rank_pivot["fractionHasCitation"])
            )
            if "modified" in summary.columns:
                pivot = pd.pivot_table(
                    summary,
                    values="modifiedSinceImport",
                    index=ranks_for_index,
                    aggfunc="sum",
                )
                rank_pivot = pd.merge(rank_pivot, pivot, on=ranks_for_index)
                pivot = pd.pivot_table(
                    summary,
                    values="modifiedThisYear",
                    index=ranks_for_index,
                    aggfunc="sum",
                )
                rank_pivot = pd.merge(rank_pivot, pivot, on=ranks_for_index)
                rank_pivot["fractionModifiedSinceImport"] = (
                    rank_pivot["modifiedSinceImport"] / rank_pivot["nameCount"]
                )
                rank_pivot["fractionModifiedThisYear"] = (
                    rank_pivot["modifiedThisYear"] / rank_pivot["nameCount"]
                )
            rank_pivot.to_csv(metrics_files[r], index=True)


if __name__ == "__main__":
    report_metrics()
