from urllib.request import urlopen
from lxml import etree
import os
import lep_config

def cleanup_articles():
    folder = lep_config.folder
    for f in os.listdir(folder):
        if f.endswith("_new.csv"):
            os.remove(os.path.join(folder, f))
