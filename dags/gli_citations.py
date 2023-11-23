import os
import pandas as pd
import gli_config as cfg


def report_citations():
    print(f"{cfg.summary_file}")
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

        pivot = pd.pivot_table(
            summary[summary["year"] > "2021"],
            values="ID",
            index=["year", "family", "citation"],
            aggfunc=pd.Series.nunique,
        )
        pivot = pivot[(pivot["ID"] > 9)].sort_index(
            level=[0, 1, 2], ascending=[False, True, True]
        )

        with open(cfg.citation_file, "w", encoding="utf8") as report:
            year = ""
            family = ""
            for idx, value in pivot.groupby(level=[0, 1, 2], sort=False):
                y, f, c = idx
                if y != year:
                    year = y
                    family = ""
                    report.write(f"\n**{year}**\n")
                if f != family:
                    family = f
                    report.write(f"* **{family}**\n")
                report.write(f"    * {c}\n")
