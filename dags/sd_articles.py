import urllib.request
from lxml import etree
import csv
import os
import re
import lep_config


def get_sd_articles(feeds=[]):
    folder = lep_config.folder
    if not os.path.exists(folder):
        os.mkdir(folder)

    pattern_1 = re.compile(r"^.* Volume ([^,]*), Issue ([^<]*).* Author.*: ([^<]*).*")
    pattern_2 = re.compile(r"^.*Author.*: ([^<]*).*")
    pages = ""
    image = ""

    for feed in feeds:
        name = feed["name"]
        shortname = feed["shortname"]
        rss = feed["rss"]

        print(f"Processing {name}")

        file_latest = os.path.join(folder, f"{shortname}.csv")

        with open(file_latest, "w", newline="", encoding="utf8") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(
                ["journal", "url", "title", "authors", "issue", "pages", "image"]
            )

            req = urllib.request.Request(
                rss,
                data=None,
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:109.0) Gecko/20100101 Firefox/116.0"
                },
            )
            page = urllib.request.urlopen(req)
            xml = page.read()
            tree = etree.XML(xml)

            items = tree.xpath("//item")
            for item in items:
                title = item.xpath("./title")[0].text.strip()
                if "lepidoptera" in title.lower():
                    url = item.xpath("./link")[0].text.strip()
                    description = item.xpath("./description")[0].text.strip()
                    match = pattern_1.match(description)
                    if match is not None:
                        issue = f"{match.group(1)}: {match.group(2)}"
                        authors = match.group(3)
                    else:
                        issue = ""
                        match = pattern_2.match(description)
                        if match is not None:
                            authors = match.group(1)
                        else:
                            authors = ""
                    record = [name, url, title, authors, issue, pages, image]
                    writer.writerow(record)
