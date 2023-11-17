from urllib.request import urlopen
from lxml import etree
import csv
import os
import lep_config


def get_zt_issues():
    folder = lep_config.folder
    zt_folder = os.path.join(folder, "zootaxa")
    page = urlopen("https://www.mapress.com/zt/issue/archive")
    html = page.read().decode("utf-8")
    tree = etree.HTML(html)

    if not os.path.exists(zt_folder):
        if not os.path.exists(folder):
            os.mkdir(folder)
        os.mkdir(zt_folder)

    with open(os.path.join(zt_folder, "issues_latest.csv"), 'w', newline='', encoding='utf8') as f:
        writer= csv.writer(f, delimiter=',')
        writer.writerow(["title", "series", "url"])
        issues = tree.xpath("//div[@class='obj_issue_summary']")
        for _, issue in zip(range(20), issues):
            title = issue.xpath(".//a[@class='title']")[0].text.strip()
            series = issue.xpath(".//div[@class='series']")[0].text.strip()
            url = issue.xpath(".//a[@class='title']")[0].attrib["href"].strip()
            writer.writerow([title, series, url])