import os
import gli_config as cfg
from urllib.request import urlopen
import pandas as pd
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
    
    return f"| {name} | {values['scientificName']} | {round(values['year'])} | {format_percent(values['fractionSynonyms'], values['significantSynonyms'])}% | {format_percent(values['fractionModifiedSinceImport'], values['significantModifiedSinceImport'])}% | {format_percent(values['fractionHasCitation'], values['significantHasCitation'])}% |"

def update_metadata():
    if os.path.exists(cfg.coldp_path) and os.path.isdir(cfg.coldp_path):
        page = urlopen(cfg.metadata_url)
        text = page.read().decode("utf-8")
        metadata = yaml.safe_load(text)
        metadata["version"] = f"1.1.{datetime.datetime.today().strftime('%Y.%j')[2:]}"
        metadata["issued"] = datetime.datetime.today().strftime('%Y-%m-%d')

        description = metadata["description"]
        
        eyecatcher = "\n\n**Summary statistics**\n\n"
        if eyecatcher in description:
            description = description[0:description.index(eyecatcher)]

        exclusions = []
        for s in [m.group(1) for m in re.finditer(r"\* \*\*([^\*]*)\*\*", description)]:
            exclusions += s.split(", ")
        print(f"Exclusions: {', '.join(exclusions)}")

        strengths = [m.group(1) for m in re.finditer(r"[^\*] \*\*([^\*]*)\*\*", description)]
        print(f"Strengths: {', '.join(strengths)}")

        table = "| Family | Names | Mean year | Synonyms | Modified | Citation |\n" \
                "| --- | ---: | :---: | ---: | ---: | ---: |\n"
        
        families = pd.read_csv(cfg.family_file, keep_default_na=False, sep=",")
        families.loc[families["superfamily"] == "", ["superfamily"]] = all_z
        families.loc[families["family"] == "", ["family"]] = all_z
        families["exclusion"] = families["family"].isin(exclusions)
        families["strength"] = families["family"].isin(strengths)
        families["subfamily"] = all_a
        families["tribe"] = all_a

        threshold_synonym = families["fractionSynonyms"].mean() + families["fractionSynonyms"].std()
        threshold_modified = families["fractionModifiedSinceImport"].mean() + families["fractionModifiedSinceImport"].std()
        threshold_citation = families["fractionHasCitation"].mean() + families["fractionHasCitation"].std()

        subfamilies = pd.read_csv(cfg.subfamily_file, keep_default_na=False, sep=",")
        subfamilies["tribe"] = all_a
        subfamilies["exclusion"] = False
        subfamilies["strength"] = subfamilies["subfamily"].isin(strengths)
        strong_subfamilies = subfamilies[subfamilies["subfamily"].isin(strengths)][list(families.columns.values)]

        tribes = pd.read_csv(cfg.tribe_file, keep_default_na=False, sep=",")
        tribes["exclusion"] = False
        tribes["strength"] = tribes["tribe"].isin(strengths)
        strong_tribes = tribes[tribes["tribe"].isin(strengths)][list(families.columns.values)]

        families = pd.concat([families, strong_subfamilies, strong_tribes], axis=0)
        families.sort_values(["superfamily", "family", "subfamily", "tribe"], inplace=True)
        families.loc[families["superfamily"] == all_z, ["superfamily", "family"]] = ["Unplaced to superfamily", ""]
        families.loc[families["family"] == all_z, ["family"]] = "Unplaced to family"
        families.replace(all_a, "", regex=False, inplace=True)

        families["significantSynonyms"] = families["fractionSynonyms"].gt(threshold_synonym)
        families["significantModifiedSinceImport"] = families["fractionModifiedSinceImport"].gt(threshold_modified)
        families["significantHasCitation"] = families["fractionHasCitation"].gt(threshold_citation)

        families.to_csv(os.path.join(cfg.scratch_folder, "family_data.csv"), sep=',')

        rows = families.apply(get_row, axis=1)

        for sf in cfg.superfamilies + [""]:
            block = pd.Series(rows[families["superfamily"] == sf]).str.cat(sep='\n')
            if block:
                table += f"\n{block}"

        explanation = "The following statistics indicate progress towards cleaning the Global Lepidoptera Index. For each family:\n\n" \
        "* **Names** is the count of scientific names included within the family.\n" \
        "* **Mean year** is the arithmetic mean of the publication years for scientific names within the family - a higher value may mean that more recent taxonomic work has been included.\n" \
        "* **Synonyms** is the percentage of scientific names that are identified as synonyms or alternative combinations for an accepted species - a higher value may mean that more taxonomic revisionary work has been included.\n" \
        "* **Modified** is the percentage of scientific names that have been added or modified since data were imported from the historical LepIndex dataset - higher values indicate more work on the family within the Global Lepidoptera Index.\n" \
        "* **Citation** is the percentage of scientific names that are associated with a publication reference - higher values indicate a greater confidence that the names have been reviewed.\n\n" \
        "Bold taxon names highlight groups which have been significantly edited in the Global Lepidoptera Index. Italicised taxon names indicate groups which are not actively maintained in this dataset. Bold values for percentages indicate that the value is more than one standard deviation above the mean.\n\n"

        metadata["description"] = f"{description}{eyecatcher}{explanation}{table}"

        with open(cfg.metadata_file, "w", encoding="utf8") as file:
            yaml.dump(metadata, file)