import urllib.request
from lxml import etree
import csv
import os
import lep_config

def get_ecolmont_articles():
    folder = lep_config.folder
    file_latest = os.path.join(folder, "ecolmont.csv")
    
    if not os.path.exists(folder):
        os.mkdir(folder)
    with open(file_latest, "w", newline='', encoding='utf8') as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(["journal", "url", "title", "authors", "issue", "pages", "image"])
        req = urllib.request.Request("https://www.biotaxa.org/em/issue/current", data=None, headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:109.0) Gecko/20100101 Firefox/116.0'})
        page = urllib.request.urlopen(req)
        html = page.read().decode("utf-8").replace("<strong>", "").replace("</strong>", "").replace("<em>", "!@em@!").replace("</em>", "!@/em@!").replace("<span>Page range:</span>", "")
        tree = etree.HTML(html)
        issue = tree.xpath("//span[@aria-current='page']")[0].text.strip()
        articles = tree.xpath("//div[@class='obj_article_summary']")
        for article in articles:
            title = article.xpath(".//h3[@class='title']//a/p")[0].text.strip().replace("!@", "<").replace("@!", ">").replace("  ", " ")
            if "lepidoptera" in title.lower():
                url = article.xpath(".//h3[@class='title']//a")[0].attrib["href"].strip()
                authors = article.xpath(".//div[@class='authors']")[0].text.strip()
                pages = article.xpath(".//div[@class='pages']")[0].text.strip()     
                images = article.xpath(".//img")
                if images is not None and len(images) > 0: 
                    image = images[0].attrib["src"].strip()
                else:
                    image = ""
                writer.writerow(["Ecologica Montenegrina", url, title, authors, issue[1], pages, image])