import os
import gli_config
from urllib.request import urlopen
import datetime
import yaml

def report():
    folder = gli_config.folder
    for f in os.listdir(folder):
        filepath = os.path.join(folder, f)
        if os.path.isdir(filepath):
            metadata_file = os.path.join(filepath, "metadata.yaml")
            page = urlopen(gli_config.metadata_url)
            text = page.read().decode("utf-8")
            metadata = yaml.safe_load(text)
            metadata["version"] = f"1.1.{datetime.datetime.today().strftime('%Y.%j')[2:]}"
            metadata["issued"] = datetime.datetime.today().strftime('%Y-%m-%d')
            metadata["description"] += \
                "\n\nThe Global Lepidoptera Index is not at present actively maintained for the following Lepidoptera groups since these are maintained in other public datasets" \
                "\n<strong>Nepticuloidea</strong>: <a href='https://www.checklistbank.org/dataset/1172/about'>Nepticulidae and Opostegidae of the World</a>" \
                "\n<strong>Tineidae</strong>: <a href='https://www.checklistbank.org/dataset/1031/about'>Global taxonomic database of Tineidae (Lepidoptera)</a>" \
                "\n<strong>Gracillariidae</strong>: <a href='https://www.checklistbank.org/dataset/1049/about'>Global Taxonomic Database of Gracillariidae</a>" \
                "\n<strong>Gelechiidae</strong>: <a href='https://www.checklistbank.org/dataset/2362/about'>Catalogue of World Gelechiidae</a>" \
                "\n<strong>Alucitoidea</strong>: <a href='https://www.checklistbank.org/dataset/2207/about'>Catalogue of the Alucitoidea of the World</a>" \
                "\n<strong>Pterophoroidea</strong>: <a href='https://www.checklistbank.org/dataset/1199/about'>Catalogue of the Pterophoroidea of the World</a>" \
                "\n<strong>Tortricidae</strong>: <a href='https://www.checklistbank.org/dataset/219318/about'>World Catalogue of the Tortricidae</a>" \
                "\n<strong>Sesiidae</strong>: <a href='https://www.checklistbank.org/dataset/55353/about'>Checklist of the Sesiidae of the world</a>" \
                "\n<strong>Papilionidae and Pieridae</strong>: <a href='https://www.checklistbank.org/dataset/1046/about'>Global Butterfly Information System</a>" \
            
            with open(metadata_file, "w", encoding="utf8") as file:
                yaml.dump(metadata, file)
