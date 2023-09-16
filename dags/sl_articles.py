from urllib.request import urlopen
from lxml import etree
import csv
import os
import lep_config

def get_shilap_articles():
    folder = lep_config.folder
    file_latest = os.path.join(folder, "shilap.csv")
    
    if not os.path.exists(folder):
        os.mkdir(folder)
    with open(file_latest, "w", newline='', encoding='utf8') as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(["journal", "url", "title", "authors", "issue", "pages", "image"])
        page = urlopen("https://shilap.org/revista/issue/view/15")
        html = page.read().decode("utf-8")
        tree = etree.HTML(html)
        issue = tree.xpath("//span[@aria-current='page']")[0].text.strip()
        articles = tree.xpath("//div[@class='obj_article_summary']")
        for article in articles:
            title = article.xpath(".//h3[@class='title']/a")[0].text.strip()
            url = article.xpath(".//h3[@class='title']/a")[0].attrib["href"].strip()
            authors = article.xpath(".//div[@class='authors']")[0].text.strip()
            pages = article.xpath(".//div[@class='pages']")[0].text.strip()
            image = ""
            record = ["SHILAP", url, title, authors, issue, pages, image]
            writer.writerow(record)
