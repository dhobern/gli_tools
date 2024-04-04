from urllib.request import urlopen
from lxml import etree
import csv
import os
import lep_config


def get_fee_articles():
    folder = lep_config.folder
    file_latest = os.path.join(folder, "fee.csv")

    if not os.path.exists(folder):
        os.mkdir(folder)
    with open(file_latest, "w", newline="", encoding="utf8") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(
            ["journal", "url", "title", "authors", "issue", "pages", "image"]
        )
        page = urlopen("https://www.biosoil.ru/FEE/Issues/")
        html = (
            page.read()
            .decode("utf-8")
            .replace("<strong>", "")
            .replace("</strong>", "||")
            .replace("<b>", "")
            .replace("</b>", "||")
            .replace("<em>", "!@em@!")
            .replace("</em>", "!@/em@!")
        )
        tree = etree.HTML(html)
        container = tree.xpath("//div[@class='col-lg-10']")[0]
        for node in container.iter():
            if node.tag == "h2":
                issue = node.text
            elif node.tag == "p":
                parts = node.xpath(".//a")[0].text.split("||")
                title = (
                    parts[1]
                    .strip()
                    .replace("!@", "<")
                    .replace("@!", ">")
                    .replace("\n", " ")
                    .replace("  ", " ")
                )
                if "lepidoptera" in title.lower():
                    authors = parts[0].strip()
                    url = (
                        "https://www.biosoil.ru"
                        + node.xpath(".//a")[0].attrib["href"].strip()
                    )
                    pages = ""
                    image = ""
                    record = [
                        "Far Eastern Entomologist",
                        url,
                        title,
                        authors,
                        issue,
                        pages,
                        image,
                    ]
                    writer.writerow(record)
