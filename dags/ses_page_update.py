from urllib.request import urlopen
from lxml import etree
import csv
import os
import lep_config
from airflow.exceptions import AirflowFailException


def get_ses_page_update():
    folder = lep_config.folder
    file_latest = os.path.join(folder, "ses.csv")
    last_date_file = os.path.join(folder, "ses_date.txt")
    eyecatcher = "Latest update: "
    url = "http://www.sesiidae.net/Checklst.htm"

    if not os.path.exists(folder):
        os.mkdir(folder)
    with open(file_latest, "w", newline="", encoding="utf8") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(
            ["journal", "url", "title", "authors", "issue", "pages", "image"]
        )
        page = urlopen(url)
        html = page.read().decode("iso-8859-1")
        offset = html.find(eyecatcher)
        if offset < 0:
            raise AirflowFailException("ERROR: Could not find update date")
        else:
            offset += len(eyecatcher)
            date = html[offset : html.find("-20", offset) + 5]
            last_date = ""
            if os.path.exists(last_date_file):
                with open(last_date_file, encoding="utf8", newline="") as ldf:
                    last_date = ldf.readline()
            if last_date != date:
                with open(last_date_file, "w", encoding="utf8", newline="") as ldf:
                    ldf.write(date)
                    record = [
                        "Sesiidae.net",
                        url,
                        f"Sesiidae.net (Update: {date})",
                        "Pühringer, F. & Kallies, A.",
                        date,
                        "",
                        "https://api.checklistbank.org/dataset/55353/logo?size=large",
                    ]
                    writer.writerow(record)
