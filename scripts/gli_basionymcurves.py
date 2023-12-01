import os
from urllib.request import urlopen
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re


basionym_years_file = "gli_basionyms.csv"
sample_families_folder = "samples"
rolling_window_years = 11
start_year = 1758
end_year = 2023
normalisation_peak_start = 1900
normalisation_peak_end = 1950
lepindex_curation_decline_year = 1975

curves = pd.DataFrame()
curves["year"] = pd.Series(range(start_year, end_year + 1))
curves["current"] = 0

standard = ["current", "gliLegacy", "gliUpdated"]
families = []

for f in os.listdir(sample_families_folder):
    dataset, ext = os.path.splitext(f)
    if ext == ".csv":
        print(f"Processing {dataset}")
        names = pd.read_csv(
            os.path.join("samples", f), encoding="utf8", sep=",", dtype="str"
        )
        names["year"] = names["authorship"].apply(
            lambda x: re.sub(r"[^0-9]*([1-2][0-9]{3})?.*", r"\1", str(x))
        )
        names["year"] = names["year"].apply(lambda x: np.nan if x == "" else int(x))
        names = names[
            (names["rank"].isin(["species", "subspecies", "variety", "form"]))
            & (names["ID"] == names["basionymID"])
            & ~(names["year"].isna())
        ]
        counts = pd.pivot_table(
            names,
            values="ID",
            index="year",
            aggfunc=pd.Series.nunique,
        )
        counts.rename(columns={"ID": dataset}, inplace=True)
        curves = pd.merge(curves, counts, how="left", on="year")
        curves[dataset].fillna(0, inplace=True)
        curves["current"] = curves["current"] + curves[dataset]
        families.append(dataset)

gli = pd.read_csv(basionym_years_file, encoding="utf8", sep=",")
gli.fillna(0, inplace=True)
gli["gliLegacy"] = gli["exclusion"] + gli["other"]
gli.rename(columns={"strength": "gliUpdated"}, inplace=True)

curves = pd.merge(
    curves, gli[["year", "gliUpdated", "gliLegacy"]], how="left", on="year"
)
curves.fillna(0, inplace=True)
curves["current"] = curves["current"] + curves["gliUpdated"]

for dataset in standard + families:
    rolling_column = f"{dataset}_rolling"
    percentage_column = f"{dataset}_percentage"
    curves[percentage_column] = 100 * curves[dataset] / curves[dataset].sum()
    curves[rolling_column] = (
        curves[dataset].rolling(rolling_window_years, center=True, min_periods=1).mean()
    )
    sum = curves[rolling_column].sum()
    curves[rolling_column] = 100 * curves[rolling_column] / sum

legacy_max = curves[
    (curves["year"] > normalisation_peak_start)
    & (curves["year"] < normalisation_peak_end)
]["gliLegacy_rolling"].max()
current_max = curves[
    (curves["year"] > normalisation_peak_start)
    & (curves["year"] < normalisation_peak_end)
]["current_rolling"].max()
curves["current_rolling_normalised"] = (
    curves["current_rolling"] * legacy_max / current_max
)

curves.to_csv("basionymCurves.csv", index=False)

fig = plt.figure(figsize=(20, 12))
ax = fig.add_subplot()
ax.set_title("Species-grade basionyms by year", fontsize=20)
ax.set_xlabel("Year")
ax.set_ylabel("Percentage of basionyms per year")
label = (
    f"Legacy families (Area under curve: {curves['gliLegacy_percentage'].sum():.2f})"
)
ax.plot(
    curves["year"],
    curves["gliLegacy_percentage"],
    label=label,
    lw=3.0,
    color="red",
)
label = f"Curated families (Area under curve: {curves['current_percentage'].sum():.2f})"
ax.plot(
    curves["year"],
    curves["current_percentage"],
    label=label,
    lw=3.0,
)
ax.legend(loc="upper left", fontsize=12)
plt.savefig("percentageBasionymCurves.png")

fig = plt.figure(figsize=(20, 12))
ax = fig.add_subplot()
major = np.arange(start_year, end_year, 50)
minor = np.arange(start_year, end_year, 10)
ax.minorticks_on()
ax.set_xticks(major)
ax.set_xticks(minor, minor=True)
ax.grid(which="major", axis="x", alpha=0.8)
ax.grid(which="minor", axis="x", alpha=0.3)
ax.set_title(
    f"Species-grade basionyms by year ({rolling_window_years}-year rolling mean of percentage of names first published in each year)",
    fontsize=20,
)
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Percentage of basionyms per year", fontsize=12)
label = f"Legacy families ({curves['gliLegacy'].sum():.0f} names - Area under curve: {curves['gliLegacy_rolling'].sum():.2f})"
ax.plot(
    curves["year"],
    curves["gliLegacy_rolling"],
    label=label,
    lw=3.0,
    color="red",
)
ax.legend(loc="upper left", fontsize=12)
plt.savefig("rollingBasionymCurves_legacy.png")
label = f"Curated families ({curves['current'].sum():.0f} names - Area under curve: {curves['current_rolling'].sum():.2f})"
ax.plot(
    curves["year"],
    curves["current_rolling"],
    label=label,
    color="orange",
    lw=3.0,
)
ax.legend(loc="upper left", fontsize=12)
plt.savefig("rollingBasionymCurves_legacy+curated.png")
label = f"Curated families rescaled to fit (Area under curve: {curves['current_rolling_normalised'].sum():.2f})"
ax.plot(
    curves["year"],
    curves["current_rolling_normalised"],
    label=label,
    color="green",
    lw=3.0,
)
ax.legend(loc="upper left", fontsize=12)
plt.savefig("rollingBasionymCurves_scaled.png")
curves["excess"] = curves["current_rolling_normalised"] - curves["gliLegacy_rolling"]
excess = curves[
    (curves["year"] > lepindex_curation_decline_year) & (curves["excess"] > 0)
]["excess"].sum()
normalised = curves["current_rolling_normalised"].sum()
uplift = (normalised / (normalised - excess)) - 1
label = f"LepIndex legacy content"
ax.fill_between(
    curves["year"],
    curves["gliLegacy_rolling"],
    color="red",
    label=label,
    alpha=0.2,
    interpolate=True,
)
label = f"Curation effect ({100 * ((normalised / (normalised - excess)) - 1):.2f}% added - estimated {curves['gliLegacy'].sum() * uplift:.0f} names missing from legacy families)"
ax.fill_between(
    curves["year"],
    curves["gliLegacy_rolling"],
    curves["current_rolling_normalised"],
    where=(
        (curves["year"] > lepindex_curation_decline_year)
        & (curves["current_rolling_normalised"] > curves["gliLegacy_rolling"])
    ),
    color="green",
    label=label,
    alpha=0.2,
    interpolate=True,
)
ax.legend(loc="upper left", fontsize=12)
plt.savefig("rollingBasionymCurves.png")
for c in ax.get_children():
    if "PolyCollection" in f"{c}":
        c.remove()
for f in families:
    ax.plot(
        curves["year"],
        curves[f"{f}_rolling"],
        label=f,
        lw=1.0,
    )
ax.legend(loc="upper left", fontsize=12)
plt.savefig("rollingBasionymCurves_withSamples.png")
