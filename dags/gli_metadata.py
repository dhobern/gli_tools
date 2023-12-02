import os
import gli_config as cfg
from urllib.request import urlopen
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import datetime
import yaml
import re

all_a = "Aaaaa"
all_z = "Zzzzz"


def format_name(name, values):
    if values["strength"]:
        return f"**{name}**"
    if values["exclusion"]:
        return f"*[{name}]*"
    return name


def format_percent(value, significant):
    if significant:
        return f"**{(value * 100):.1f}**"
    return f"{(value * 100):.1f}"


def get_row(values):
    if values["tribe"]:
        name = f"{values['superfamily']}: {values['family']}: {values['subfamily']}: {format_name(values['tribe'], values)}"
    elif values["subfamily"]:
        name = f"{values['superfamily']}: {values['family']}: {format_name(values['subfamily'], values)}"
    elif values["family"]:
        name = f"{values['superfamily']}: {format_name(values['family'], values)}"
    else:
        name = values["superfamily"]

    return f"| {name} | {values['nameCount']} | {values['speciesCount']} | {round(values['year'])} | {format_percent(values['fractionSynonyms'], values['significantSynonyms'])}% | {format_percent(values['fractionModifiedSinceImport'], values['significantModifiedSinceImport'])}% | {format_percent(values['fractionHasCitation'], values['significantHasCitation'])}% |"


def update_metadata():
    if os.path.exists(cfg.coldp_path) and os.path.isdir(cfg.coldp_path):
        page = urlopen(cfg.metadata_url)
        text = page.read().decode("utf-8")
        metadata = yaml.safe_load(text)
        metadata["version"] = f"1.1.{datetime.datetime.today().strftime('%Y.%j')[2:]}"
        metadata["issued"] = datetime.datetime.today().strftime("%Y-%m-%d")

        description = metadata["description"]

        eyecatcher = "\n\n**Summary statistics**\n\n"
        if eyecatcher in description:
            description = description[0 : description.index(eyecatcher)]

        exclusions = []
        for s in [m.group(1) for m in re.finditer(r"\* \*\*([^\*]*)\*\*", description)]:
            exclusions += s.split(", ")
        print(f"Exclusions: {', '.join(exclusions)}")

        strengths = [
            m.group(1) for m in re.finditer(r"[^\*] \*\*([^\*]*)\*\*", description)
        ]
        print(f"Strengths: {', '.join(strengths)}")

        table = (
            "| Family | Names | Species | Mean year | Synonyms | Modified | Citation |\n"
            "| --- | ---: | ---: | :---: | ---: | ---: | ---: |"
        )

        families = pd.read_csv(cfg.family_file, keep_default_na=False, sep=",")
        families.loc[families["superfamily"] == "", ["superfamily"]] = all_z
        families.loc[families["family"] == "", ["family"]] = all_z
        families["exclusion"] = families["family"].isin(exclusions)
        families["strength"] = families["family"].isin(strengths)
        families["subfamily"] = all_a
        families["tribe"] = all_a

        threshold_synonym = (
            families["fractionSynonyms"].mean() + families["fractionSynonyms"].std()
        )
        threshold_modified = (
            families["fractionModifiedSinceImport"].mean()
            + families["fractionModifiedSinceImport"].std()
        )
        threshold_citation = (
            families["fractionHasCitation"].mean()
            + families["fractionHasCitation"].std()
        )

        subfamilies = pd.read_csv(cfg.subfamily_file, keep_default_na=False, sep=",")
        subfamilies["tribe"] = all_a
        subfamilies["exclusion"] = False
        subfamilies["strength"] = subfamilies["subfamily"].isin(strengths)
        strong_subfamilies = subfamilies[subfamilies["subfamily"].isin(strengths)][
            list(families.columns.values)
        ]

        tribes = pd.read_csv(cfg.tribe_file, keep_default_na=False, sep=",")
        tribes["exclusion"] = False
        tribes["strength"] = tribes["tribe"].isin(strengths)
        strong_tribes = tribes[tribes["tribe"].isin(strengths)][
            list(families.columns.values)
        ]

        families = pd.concat([families, strong_subfamilies, strong_tribes], axis=0)
        families.sort_values(
            ["superfamily", "family", "subfamily", "tribe"], inplace=True
        )
        families.loc[families["superfamily"] == all_z, ["superfamily", "family"]] = [
            "Unplaced to superfamily",
            "",
        ]
        families.loc[families["family"] == all_z, ["family"]] = "Unplaced to family"
        families.replace(all_a, "", regex=False, inplace=True)

        families["significantSynonyms"] = families["fractionSynonyms"].gt(
            threshold_synonym
        )
        families["significantModifiedSinceImport"] = families[
            "fractionModifiedSinceImport"
        ].gt(threshold_modified)
        families["significantHasCitation"] = families["fractionHasCitation"].gt(
            threshold_citation
        )

        families.to_csv(os.path.join(cfg.scratch_folder, "family_data.csv"), sep=",")

        rows = families.apply(get_row, axis=1)

        for sf in cfg.superfamilies + [""]:
            block = pd.Series(rows[families["superfamily"] == sf]).str.cat(sep="\n")
            if block:
                table += "\n" + block

        order = pd.read_csv(cfg.order_file, keep_default_na=False, sep=",")
        table += f"\n| **ALL LEPIDOPTERA** | {order['nameCount'][0]} | {order['speciesCount'][0]} | {round(order['year'][0])} | {format_percent(order['fractionSynonyms'][0], False)}% | {format_percent(order['fractionModifiedSinceImport'][0], False)}% | {format_percent(order['fractionHasCitation'][0], False)}% |"

        explanation = (
            "The following statistics indicate progress towards cleaning the Global Lepidoptera Index. For each taxon, counts are based on all accepted and synonymised names at genus rank or lower. Columns are as follows:\n\n"
            "* **Names** is the count of scientific names included within the taxon.\n"
            "* **species** is the count of accepted species included within the taxon.\n"
            "* **Mean year** is the arithmetic mean of the publication years for scientific names within the taxon - a higher value may mean that more recent taxonomic work has been included.\n"
            "* **Synonyms** is the percentage of scientific names that are identified as synonyms or alternative combinations for an accepted species - a higher value may mean that more taxonomic revisionary work has been included.\n"
            "* **Modified** is the percentage of scientific names that have been added or modified since data were imported from the historical LepIndex dataset - higher values indicate more work on the family within the Global Lepidoptera Index.\n"
            "* **Citation** is the percentage of scientific names that are associated with a publication reference - higher values indicate a greater confidence that the names have been reviewed.\n\n"
            "Bold taxon names highlight groups which have been significantly edited in the Global Lepidoptera Index. Italicised taxon names indicate groups which are not actively maintained in this dataset. Bold values for percentages indicate that the value is more than one standard deviation above the mean.\n\n"
        )

        citations = ""

        with open(cfg.citation_report, encoding="utf8") as citation_file:
            citation_list = citation_file.readlines()
            citations = (
                "\n\n**References**\n\nThe following publications have each contributed a significant number of updates to the Global Lepidoptera Index in years following 2021. In each case, at least 10 species names from the specified family were updated using the named publication in the specified year.\n"
                + "".join(citation_list)
            )

        metadata[
            "description"
        ] = f"{description}{eyecatcher}{explanation}{table}{citations}"

        with open(cfg.description_file, "w", encoding="utf8") as description_file:
            description_file.write(f"{metadata['description']}\n")

        with open(cfg.metadata_file, "w", encoding="utf8") as file:
            yaml.dump(metadata, file)

        summary = pd.read_csv(
            cfg.summary_file, dtype=str, keep_default_na=False, sep=","
        )
        summary["year"] = summary["authorship"].apply(
            lambda x: re.sub(r"[^0-9]*([1-2][0-9]{3})?.*", r"\1", str(x))
        )
        summary["year"] = summary["year"].apply(lambda x: np.nan if x == "" else int(x))

        summary = summary[
            (summary["rank"].isin(["species", "subspecies", "variety", "form"]))
            & (summary["nameID"] == summary["basionymID"])
            & ~(summary["year"] == np.nan)
            & (summary["year"] >= 1758)
        ]
        summary["strength"] = 0
        summary.loc[
            (summary["superfamily"].isin(strengths))
            | (summary["family"].isin(strengths))
            | (summary["subfamily"].isin(strengths))
            | (summary["tribe"].isin(strengths)),
            ["strength"],
        ] = 1
        summary["exclusion"] = 0
        summary.loc[
            (summary["superfamily"].isin(exclusions))
            | (summary["family"].isin(exclusions))
            | (summary["subfamily"].isin(exclusions))
            | (summary["tribe"].isin(exclusions)),
            ["exclusion"],
        ] = 1
        curves = pd.DataFrame()
        curves["year"] = pd.Series(range(1758, 2024))
        strong = pd.pivot_table(
            summary[summary["strength"] == 1],
            values="strength",
            index="year",
            aggfunc="sum",
        )
        curves = pd.merge(curves, strong, how="left", on="year")
        excluded = pd.pivot_table(
            summary[summary["exclusion"] == 1],
            values="exclusion",
            index="year",
            aggfunc="sum",
        )
        curves = pd.merge(curves, excluded, how="left", on="year")
        other = pd.pivot_table(
            summary[(summary["strength"] == 0) & (summary["exclusion"] == 0)],
            values="scientificName",
            index="year",
            aggfunc=pd.Series.nunique,
        )
        other.rename(columns={"scientificName": "other"}, inplace=True)
        curves = pd.merge(curves, other, how="left", on="year")
        curves["rollingStrong"] = (
            curves["strength"].rolling(11, center=True, min_periods=1).mean()
        )
        curves["rollingExcluded"] = (
            curves["exclusion"].rolling(11, center=True, min_periods=1).mean()
        )
        curves["rollingOther"] = (
            curves["other"].rolling(11, center=True, min_periods=1).mean()
        )
        curves["rollingLegacy"] = curves["rollingExcluded"] + curves["rollingOther"]
        curves["percentLegacy"] = (
            100 * curves["rollingLegacy"] / curves["rollingLegacy"].sum()
        )
        curves["percentStrong"] = (
            100 * curves["rollingStrong"] / curves["rollingStrong"].sum()
        )

        curves.to_csv(cfg.basionym_file)

        fig = plt.figure(figsize=(12, 8))
        plt.title("Species-rank basionyms by year (11-year rolling)")
        plt.xlabel("Year")
        plt.ylabel("Percentage of basionyms per year")
        plt.plot(
            curves["year"], curves["percentLegacy"], color="red", label="Incomplete"
        )
        plt.plot(
            curves["year"], curves["percentStrong"], color="green", label="Updated"
        )
        plt.legend(loc="upper left")
        plt.savefig(cfg.basionym_chart)


if __name__ == "__main__":
    update_metadata()
