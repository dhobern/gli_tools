from urllib.request import urlopen
from lxml import etree
import csv
import os
import re
import lep_config

def get_zn_articles():
    folder = lep_config.folder
    file_latest = os.path.join(folder, "zn.csv")
    
    if not os.path.exists(folder):
        os.mkdir(folder)
    with open(file_latest, "w", newline='', encoding='utf8') as f:
        zoonova_site = "https://zoonova.afriherp.org/"
        writer = csv.writer(f, delimiter=",")
        writer.writerow(["journal", "url", "title", "authors", "issue", "pages", "image"])
        page = urlopen(zoonova_site)
        html = page.read().decode("utf-8").replace("<em>", "!@em@!").replace("</em>", "!@/em@!").replace("\n", " ")
        html = re.sub(r" +", " ", html)
        html = re.sub(r"</tr> *<td", r"</tr><tr><td", html)
        print(html.count("<tr>"))
        tree = etree.HTML(html)
        articles = tree.xpath("//table/tr")
        if articles is not None and len(articles) > 1:
            for article in articles[1:]:
                elements = article.xpath("./td")
                if len(elements) == 6:
                    for u in elements[1].xpath(".//p//a"):
                        url = u.attrib["href"]
                        if "doi.org" in url:
                            break
                    title = elements[1].xpath("./span")[0].text.strip().replace("!@", "<").replace("@!", ">")
                    authors = elements[2].xpath("./div")[0].text.strip()
                    issue = elements[0].xpath("./div")[0].text.strip()
                    pages = elements[3].xpath("./div")[0].text.strip()
                    record = ["ZooNova", url, title, authors, issue, pages, ""]
                    print(record)
                    writer.writerow(record)
