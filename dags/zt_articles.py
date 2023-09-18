from urllib.request import urlopen
from lxml import etree
import csv
import os
import lep_config
import logging


def extract_zt_articles():
    folder = lep_config.folder
    zt_folder = os.path.join(folder, "zootaxa")
    file_new = os.path.join(zt_folder, "issues_new.csv")
    file_articles = os.path.join(folder, "zootaxa.csv")

    if os.path.exists(file_new):
        with open(file_articles, "w", newline="", encoding="utf8") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(
                ["journal", "url", "title", "authors", "issue", "pages", "image"]
            )
            with open(file_new, newline="", encoding="utf8") as f:
                reader = csv.reader(f, delimiter=",")
                next(reader)
                for issue in reader:
                    logging.info(f"Processing issue: {issue}")
                    page = urlopen(issue[2])
                    html = (
                        page.read()
                        .decode("utf-8")
                        .replace("<strong>", "")
                        .replace("</strong>", "")
                        .replace("<em>", "!@em@!")
                        .replace("</em>", "!@/em@!")
                        .replace("<span>Page range:</span>", "")
                    )
                    tree = etree.HTML(html)
                    articles = tree.xpath("//div[@class='obj_article_summary']")
                    for article in articles:
                        title = (
                            article.xpath(".//h2[@class='title']//a")[0]
                            .text.strip()
                            .replace("!@", "<")
                            .replace("@!", ">")
                            .replace("  ", " ")
                        )
                        if "lepidoptera" in title.lower():
                            url = (
                                article.xpath(".//h2[@class='title']//a")[0]
                                .attrib["href"]
                                .strip()
                            )
                            authors = article.xpath(".//div[@class='authors']")[
                                0
                            ].text.strip()
                            pages = article.xpath(".//div[@class='pages']")[
                                2
                            ].text.strip()
                            images = article.xpath(".//img")
                            if images is not None and len(images) > 0:
                                image = images[0].attrib["src"].strip()
                            else:
                                image = ""
                            writer.writerow(
                                ["Zootaxa", url, title, authors, issue[1], pages, image]
                            )
