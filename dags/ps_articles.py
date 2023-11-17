from urllib.request import urlopen
from lxml import etree
import csv
import os
import lep_config

def get_pensoft_articles(sites = []):
    folder = lep_config.folder
    for s in sites:
        shortname = s["shortname"]
        name = s["name"]
        print(f"Processing {name} / {shortname}")

        file_latest = os.path.join(folder, f"{shortname}.csv")
        
        if not os.path.exists(folder):
            os.mkdir(folder)
        with open(file_latest, "w", newline='', encoding='utf8') as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(["journal", "url", "title", "authors", "issue", "pages", "image"])
            page = urlopen(f"https://{shortname}.pensoft.net/browse_journal_articles.php?form_name=filter_articles&sortby=0&alerts_taxon_cats=t279")
            html = page.read().decode("utf-8").replace("<i>", "!@em@!").replace("</i>", "!@/em@!").replace("<em>", "!@em@!").replace("</em>", "!@/em@!").replace('<span class="pages_icon"></span> <span>', '<span class="pages_icon">')
            tree = etree.HTML(html)
            articles = tree.xpath("//div[@class='article']")
            for article in articles:
                title = article.xpath(".//div[@class='articleHeadline']//a")[0].text.strip().replace('\ufeff', '').replace("!@", "<").replace("@!", ">").replace("  ", " ")
                pages_nodes = article.xpath(".//span[@class='pages_icon']")
                if len(pages_nodes) > 0:
                    pages = pages_nodes[0].text.strip()
                else:
                    pages = ""
                doi = article.xpath(".//div[@class='ArtDoi subLink']/a")[0].text.strip()
                url = f"https://doi.org/{doi}"
                parts = doi.split(".")
                if len(parts) > 2 and not pages:
                    issue = ".".join(parts[1:len(parts)-1])
                    pages = parts[len(parts) - 1]
                elif len(parts) > 2:
                    issue = ".".join(parts[1:len(parts)])
                else:
                    issue = doi
                authors = article.xpath(".//a[@class='authors_list_holder']")
                for i in range(len(authors)):
                    authors[i] = authors[i].text.strip()
                if len(authors) == 1:
                    authors = authors[0]
                else:
                    authors = " & ".join([", ".join(authors[0:len(authors)-1]), authors[len(authors)-1]])
                images = article.xpath(".//img")
                if images is not None and len(images) > 0: 
                    image = images[0].attrib["src"].strip()
                else:
                    image = ""
                record = [name, url, title, authors, issue, pages, image]
                writer.writerow(record)
