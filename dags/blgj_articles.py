from urllib.request import urlopen
from lxml import etree
import csv
import os
import re
import lep_config

def get_biologija_articles():
    folder = lep_config.folder
    file_latest = os.path.join(folder, "biologija.csv")
    
    if not os.path.exists(folder):
        os.mkdir(folder)
    with open(file_latest, "w", newline='', encoding='utf8') as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(["journal", "url", "title", "authors", "issue", "pages", "image"])
        page = urlopen("https://www.lmaleidykla.lt/ojs/index.php/biologija/search/search?query=Lepidoptera")
        html = page.read().decode("utf-8").replace("<strong>", "").replace("</strong>", "").replace("<em>", "!@em@!").replace("</em>", "!@/em@!").replace("<span>Page range:</span>", "")
        tree = etree.HTML(html)
        articles = tree.xpath("//div[@class='obj_article_summary']")
        for article in articles:
            title = article.xpath(".//div[@class='title']//a")[0].text.strip().replace("!@", "<").replace("@!", ">").replace("  ", " ")
            url = article.xpath(".//div[@class='title']//a")[0].attrib["href"].strip()
            authors = article.xpath(".//div[@class='authors']")[0].text.strip()
            issues = article.xpath(".//div[@class='published']")
            if len(issues) > 0:
                issue = issues[0].text.strip()
            else:
                issue = ""
            pages = ""     
            image = ""
            writer.writerow(["Biologija", url, title, authors, issue, pages, image])
