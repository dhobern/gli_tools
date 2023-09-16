from urllib.request import urlopen
from lxml import etree
import csv
import os
import datetime
import lep_config

def format_articles(email_length = 5):
    folder = lep_config.folder
    new = os.path.join(folder, "new.csv")
    date = datetime.datetime.today().strftime('%Y-%m-%d')

    for f in os.listdir(folder):
        if f.endswith("_new.csv"):
            new = os.path.join(folder, f)
            print(f"Processing {new}")
            bodies = []
            with open(new, newline='', encoding='utf8') as n:
                reader = csv.reader(n, delimiter=",")
                next(reader)
                body = ""
                count = 0
                for row in reader:
                    if row[6]:
                        body += f"\t\t<a href='{row[1]}'><img src='{row[6]}'></a>\n"
                    body += f"\t\t<h3><a href='{row[1]}'><strong>{row[2]}</strong></a></h3>\n"
                    body += f"\t\t<p>{row[3]}</p>\n"
                    if row[4]:
                        if row[5]:
                            body += f"\t\t<p>{row[0]} {row[4]}: {row[5]}</p>\n"
                        else:
                            body += f"\t\t<p>{row[0]} {row[4]}\n"
                    elif row[5]:
                        body += f"\t\t<p>{row[0]} {row[5]}\n"
                    else:
                        body += f"\t\t<p>{row[0]}"
                    count += 1
                    if count == email_length:
                        bodies.append(body)
                        body = ""
                        count = 0
                if count > 0:
                    bodies.append(body)

            if len(bodies) < 1:
                bodies.append("<html>\n\t<head></head>\n\t<body>\t\t<h2>Lepidoptera article update</h2>\n\t\t<p>None found</p>\t</body>\n</html>\n")

            for i in range(len(bodies)):
                if len(bodies) > 1:
                    tag = f"{date}, {i+1} of {len(bodies)}"
                else:
                    tag = date
                email = os.path.join(folder, f"lepidoptera_email.{f.replace('new.csv', str(i + 1))}.html")
                print(f"Writing: {email}")
                with open(email, 'w', newline='', encoding='utf8') as e:
                    e.write("<html>\n\t<head></head>\n\t<body>")
                    e.write(f"\t\t<h2>Latest Lepidoptera articles ({tag})</h2>\n")
                    e.write(bodies[i])
                    e.write("\t</body>\n</html>\n")
