import os

scratch_folder = "/home/dhobern/airflow/scratch/gli_updates"
coldp_name = "gli"
coldp_path = os.path.join(scratch_folder, coldp_name)

coldp_file = f"{coldp_path}.zip"
summary_file = f"{coldp_path}_summary.csv"
reference_file = f"{coldp_path}_references.csv"
month_file = f"{coldp_path}_months.csv"
basionym_file = f"{coldp_path}_basionyms.csv"
basionym_chart = f"{coldp_path}_basionyms.png"
citation_report = f"{coldp_path}_citations.md"
description_file = f"{coldp_path}_description.md"
metrics_file = f"{coldp_path}_metrics.csv"
order_file = f"{coldp_path}_order.csv"
superfamily_file = f"{coldp_path}_superfamilies.csv"
family_file = f"{coldp_path}_families.csv"
subfamily_file = f"{coldp_path}_subfamilies.csv"
tribe_file = f"{coldp_path}_tribes.csv"
metadata_file = os.path.join(coldp_path, "metadata.yaml")

transfer_folder = "/home/dhobern/airflow/scratch"
metadata_url = "https://api.checklistbank.org/dataset/55434.yaml"

superfamilies = [
    "Micropterigoidea",
    "Agathiphagoidea",
    "Heterobathmioidea",
    "Eriocranioidea",
    "Neopseustoidea",
    "Lophocoronoidea",
    "Hepialoidea",
    "Nepticuloidea",
    "Andesianoidea",
    "Adeloidea",
    "Tischerioidea",
    "Palaephatoidea",
    "Tineoidea",
    "Gracillarioidea",
    "Yponomeutoidea",
    "Urodoidea",
    "Simaethistoidea",
    "Douglasioidea",
    "Schreckensteinioidea",
    "Choreutoidea",
    "Immoidea",
    "Galacticoidea",
    "Tortricoidea",
    "Zygaenoidea",
    "Cossoidea",
    "Gelechioidea",
    "Whalleyanoidea",
    "Thyridoidea",
    "Hyblaeoidea",
    "Calliduloidea",
    "Alucitoidea",
    "Epermenioidea",
    "Carposinoidea",
    "Pterophoroidea",
    "Papilionoidea",
    "Pyraloidea",
    "Mimallonoidea",
    "Drepanoidea",
    "Lasiocampoidea",
    "Bombycoidea",
    "Geometroidea",
    "Noctuoidea",
]
