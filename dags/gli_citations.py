import os
import pandas as pd
import gli_config as cfg


def report_citations():
    if os.path.exists(cfg.summary_file):
        summary = pd.read_csv(
            cfg.summary_file, dtype=str, keep_default_na=False, sep=","
        )
        references = pd.read_csv(
            cfg.reference_file, dtype=str, keep_default_na=False, sep=","
        )
        summary["year"] = summary["modified"].str[0:4]
        summary["month"] = summary["modified"].str[5:7]
        summary.loc[
            summary["superfamily"] == "",
            ["superfamily", "family", "subfamily", "tribe"],
        ] = "Lepidoptera"
        summary = summary.drop(summary[summary["referenceID"] == ""].index)
        summary = pd.merge(
            summary,
            references[["ID", "citation", "modified", "modifiedBy"]],
            how="left",
            left_on="referenceID",
            right_on="ID",
            suffixes=("", "_r"),
        )

        """
        pivot = pd.pivot_table(summary, values='scientificName', index=['year', 'month', 'referenceID', 'citation', 'superfamily', 'family', 'subfamily', 'tribe'],
                                aggfunc=pd.Series.nunique)
        """

        pivot = pd.pivot_table(
            summary,
            values="ID",
            index=["year", "citation", "family"],
            aggfunc=pd.Series.nunique,
        )
        pivot.to_csv(cfg.citation_file, index=True)
