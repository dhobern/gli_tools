import urllib.request
from urllib.request import urlopen
from lxml import etree
import csv
import os
import re
import lep_config

def get_jib_articles():
    folder = lep_config.folder
    file_latest = os.path.join(folder, "jib_articles.csv")
    
    if not os.path.exists(folder):
        os.mkdir(folder)
    with open(file_latest, "w", newline='', encoding='utf8') as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(["journal", "url", "title", "authors", "issue", "pages", "image"])
        req = urllib.request.Request("https://www.biotaxa.org/jib/search?query=Lepidoptera", 
                                     data=None, 
                                     headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:109.0) Gecko/20100101 Firefox/116.0'})
        page = urllib.request.urlopen(req)
        html = page.read().decode("utf-8").replace("<strong>", "").replace("</strong>", "").replace("<p>", "").replace("</p>", "").replace("<br>", "").replace("<em>", "!@em@!").replace("</em>", "!@/em@!").replace("<span>Page range:</span>", "")
        tree = etree.HTML(html)
        articles = tree.xpath("//div[@class='obj_article_summary']")
        for article in articles:
            title = article.xpath(".//h3[@class='title']//a")[0].text.strip().replace("!@", "<").replace("@!", ">").replace("  ", " ")
            url = article.xpath(".//h3[@class='title']//a")[0].attrib["href"].strip()
            authors = article.xpath(".//div[@class='authors']")[0].text.strip()
            issues = article.xpath(".//div[@class='published']")
            if len(issues) > 0:
                issue = issues[0].text.strip()
            else:
                issue = ""
            divs = article.xpath(".//div[@class='pages']")
            if len(divs) > 0:
                pages = divs[0].text.strip()
            else:
                pages = ""
            image = ""
            writer.writerow(["Journal of Insect Biodiversity", url, title, authors, issue, pages, image])
