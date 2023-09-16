import urllib.request
from lxml import etree
import csv
import os
import re
import lep_config
import ssl

def get_bioone_articles(journals = []):
    folder = lep_config.folder
    if not os.path.exists(folder):
        os.mkdir(folder)

    pattern_pages = re.compile(r".* ([0-9]+ \([0-9]+\)), ([0-9-]+).*")
    pages = ""
    image = ""
    
    for journal in journals:

        name = journal["name"]
        shortname = journal["shortname"]
        urlname = journal["urlname"]
        current_url = f"https://bioone.org/journals/{urlname}/current"
        if "filter" in journal:
            filter = journal["filter"]
        else:
            filter = True

        image = ""

        file_latest = os.path.join(folder, f"{shortname}.csv")

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        print(f"Processing {current_url}")
        
        with open(file_latest, "w", newline='', encoding='utf8') as f:

            writer = csv.writer(f, delimiter=",")
            writer.writerow(["journal", "url", "title", "authors", "issue", "pages", "image"])

            page = urllib.request.urlopen(current_url, context=ctx)
            html = page.read().decode("utf-8").replace("<em>", "!@em@!").replace("</em>", "!@/em@!").replace("<i>", "!@em@!").replace("</i>", "!@/em@!")
            tree = etree.HTML(html)

            items = tree.xpath("//div[contains(@class, 'row') and contains(@class, 'TOCLineItemRow1')]")
            for item in items:
                title = item.xpath(".//a[@class='TocLineItemAnchorText1']/span/text()")[0].strip().replace("!@", "<").replace("@!", ">")
                if title not in ["Full Issue", "Cover", "Table of Contents", "Foreword"] \
                        and (not filter or "lepidoptera" in title.lower()):
                    reference = item.xpath(".//text[@class='TOCLineItemText3']")[0].text.strip()
                    issue = ""
                    pages = ""
                    if reference:
                        match = pattern_pages.match(reference)
                        if match is not None:
                            issue = match.group(1)
                            pages = match.group(2)
                    url = item.xpath(".//text[@class='TOCLineItemText3']/a")[0].attrib['href'].strip()
                    authorship = item.xpath(".//span[contains(@class, 'TOCLineItemText2')]")
                    author_list = []
                    for author in authorship:
                        author_list.append(author.text.strip())

                    if len(author_list) > 2:
                        authors = " & ".join([", ".join(author_list[0:len(author_list)-1]), author_list[len(author_list)-1]])
                    else:
                        authors = " & ".join(author_list)

                    record = [name, url, title, authors, issue, pages, image]
                    writer.writerow(record)