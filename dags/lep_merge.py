from urllib.request import urlopen
from lxml import etree
import datetime
import os
import pandas as pd
import lep_config

def merge_articles():
    folder = lep_config.folder
    if os.path.exists(folder):
        
        date = datetime.datetime.today().strftime('%Y-%m-%d_%H:%M:%S')

        filename_merged = os.path.join(folder, "merged.csv")
        filename_new = os.path.join(folder, f"{date}_new.csv")
        
        if os.path.exists(filename_merged):
            previous = pd.read_csv(filename_merged, dtype=str, keep_default_na=False, sep=",")
            print(f"Previous merged.csv contains {len(previous)}")
        else:
            previous = None
        
        merged = None
        for f in os.listdir(folder):
            if f.endswith(".csv") and f != "merged.csv" and not f.endswith("_new.csv"):
                print(f"Processing {f}")
                batch = pd.read_csv(os.path.join(folder, f), dtype='str', keep_default_na=False, sep=",")
                if merged is None:
                    merged = batch
                else:
                    merged = pd.concat([merged, batch])
        if merged is None:
            print(f"Nothing to merge")
        else:
            print(f"New merged.csv contains {len(merged)}")
        
            if previous is not None:
                new = merged[~merged.url.isin(previous.url)]
            else:
                new = merged          

            if len(new) > 0:
                print(f"{len(new)} records are new - writing {filename_new}")
                new.to_csv(filename_new, index=False)
    
            print(f"Saving merged.csv")
            merged.to_csv(filename_merged, index= False)
