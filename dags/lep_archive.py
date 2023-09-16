from urllib.request import urlopen
from lxml import etree
import os
import datetime
import shutil
import lep_config

def archive_articles(archive_folder = ""):
    folder = lep_config.folder
    if archive_folder and os.path.exists(archive_folder):
        for f in os.listdir(folder):
            if f.endswith("_new.csv"):
                new = os.path.join(folder, f)
                print(f"Archiving {new}")
                date = datetime.datetime.today().strftime('%Y-%m-%d')
                filebase = os.path.join(archive_folder, f"lepidoptera_articles_{date}")
                index = 1
                filename = f"{filebase}.csv"
                while os.path.exists(filename):
                    filename = f"{filebase}_{index}.csv"
                    index += 1
                shutil.copy(new, filename)