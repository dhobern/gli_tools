import airflow
from airflow import DAG
from airflow.operators.python import PythonOperator
import datetime
import pendulum

import ps_articles
import sd_articles
import bo_articles
import fee_articles
import zn_articles
import sl_articles
import zt_issues
import zt_select
import zt_articles
import em_articles
import blgj_articles
import jib_articles
import lep_merge
import lep_format
import lep_archive
import lep_cleanup
import lep_email

local_tz = pendulum.timezone("Australia/Canberra")

dag = DAG(
    dag_id="lepidoptera_updates",
    start_date=datetime.datetime(2023, 8, 10, tzinfo=local_tz),
    schedule_interval="0 14 * * *",
    default_args={"email": "dhobern@gmail.com"},
    catchup=False,
)

pensoft_articles = PythonOperator(
    task_id="ps_articles",
    python_callable=ps_articles.get_pensoft_articles,
    op_kwargs={
        "sites": [
            {"name": "African Invertebrates", "shortname": "africaninvertebrates"},
            {"name": "ZooKeys", "shortname": "zookeys"},
            {"name": "Nota Lepidopterologica", "shortname": "nl"},
            {"name": "Biodoversity Data Journal", "shortname": "bdj"},
            {"name": "Deutsche Entomologische Zeitschrift", "shortname": "dez"},
            {"name": "Alpine Entomology", "shortname": "alpineentomology"},
            {"name": "Checklist", "shortname": "checklist"},
            {"name": "Evolutionary Systematics", "shortname": "evolsyst"},
            {"name": "Metabarcoding and Metagenomics", "shortname": "mbmg"},
            {"name": "Travaux", "shortname": "travaux"},
            {"name": "Caucasiana", "shortname": "caucasiana"},
            {"name": "Zoosystematics and Evolution", "shortname": "zse"},
        ]
    },
    dag=dag,
)

sciencedirect_articles = PythonOperator(
    task_id="sd_articles",
    python_callable=sd_articles.get_sd_articles,
    op_kwargs={
        "feeds": [
            {
                "name": "Journal of Asia-Pacific Entomology",
                "shortname": "apentom",
                "rss": "https://rss.sciencedirect.com/publication/science/12268615",
            },
            {
                "name": "Journal of Asia-Pacific Biodiversity",
                "shortname": "apbiodiv",
                "rss": "https://rss.sciencedirect.com/publication/science/2287884X",
            },
        ]
    },
    dag=dag,
)

bioone_articles = PythonOperator(
    task_id="bo_articles",
    python_callable=bo_articles.get_bioone_articles,
    op_kwargs={
        "journals": [
            {
                "name": "Annales Zoologici",
                "shortname": "az",
                "urlname": "annales-zoologici",
            },
            {
                "name": "Annals of the Entomological Society of America",
                "shortname": "esa",
                "urlname": "annals-of-the-entomological-society-of-america",
            },
            {
                "name": "The Canadian Entomologist",
                "shortname": "canent",
                "urlname": "the-canadian-entomologist",
            },
            {
                "name": "Entomologica Americana",
                "shortname": "americana",
                "urlname": "entomologica-americana",
            },
            {
                "name": "Entomological News",
                "shortname": "entnews",
                "urlname": "entomological-news",
            },
            {
                "name": "Florida Entomologist",
                "shortname": "florent",
                "urlname": "florida-entomologist",
            },
            {
                "name": "Insect Systematics and Diversity",
                "shortname": "isd",
                "urlname": "insect-systematics-and-diversity",
            },
            {
                "name": "Journal of the Kansas Entomological Society",
                "shortname": "jks",
                "urlname": "journal-of-the-kansas-entomological-society",
            },
            {
                "name": "The Journal of the Lepidopterists' Society",
                "shortname": "jls",
                "urlname": "the-journal-of-the-lepidopterists-society",
                "filter": False,
            },
            {
                "name": "The Pan-Pacific Entomologist",
                "shortname": "ppe",
                "urlname": "the-pan-pacific-entomologist",
            },
            {
                "name": "Proceedings of the Entomological Society of Washington",
                "shortname": "esw",
                "urlname": "proceedings-of-the-entomological-society-of-washington",
            },
            {
                "name": "Southwestern Entomologist",
                "shortname": "swent",
                "urlname": "southwestern-entomologist",
            },
            {
                "name": "Transactions of the American Entomological Society",
                "shortname": "transaes",
                "urlname": "transactions-of-the-american-entomological-society",
            },
        ]
    },
    dag=dag,
)

fareastent_articles = PythonOperator(
    task_id="fee_articles",
    python_callable=fee_articles.get_fee_articles,
    dag=dag,
)

zoonova_articles = PythonOperator(
    task_id="zn_articles",
    python_callable=zn_articles.get_zn_articles,
    dag=dag,
)

biologija_articles = PythonOperator(
    task_id="biologija_articles",
    python_callable=blgj_articles.get_biologija_articles,
    dag=dag,
)

jinsbiod_articles = PythonOperator(
    task_id="jinsbiod_articles",
    python_callable=jib_articles.get_jib_articles,
    dag=dag,
)

shilap_articles = PythonOperator(
    task_id="sl_articles",
    python_callable=sl_articles.get_shilap_articles,
    dag=dag,
)

zootaxa_issues = PythonOperator(
    task_id="zt_issues",
    python_callable=zt_issues.get_zt_issues,
    dag=dag,
)

zootaxa_select = PythonOperator(
    task_id="zt_select",
    python_callable=zt_select.select_zt_issues,
    dag=dag,
)

zootaxa_articles = PythonOperator(
    task_id="zt_articles",
    python_callable=zt_articles.extract_zt_articles,
    dag=dag,
)

ecolmont_articles = PythonOperator(
    task_id="em_articles",
    python_callable=em_articles.get_ecolmont_articles,
    dag=dag,
)

merge_articles = PythonOperator(
    task_id="merge_articles",
    python_callable=lep_merge.merge_articles,
    dag=dag,
    trigger_rule="all_done",
)

format_articles = PythonOperator(
    task_id="format_articles",
    python_callable=lep_format.format_articles,
    op_kwargs={"email_length": 10},
    dag=dag,
)

archive_articles = PythonOperator(
    task_id="archive_articles",
    python_callable=lep_archive.archive_articles,
    op_kwargs={"archive_folder": "/home/dhobern/Dropbox/LepidopteraArticles"},
    dag=dag,
)

cleanup_articles = PythonOperator(
    task_id="cleanup_articles",
    python_callable=lep_cleanup.cleanup_articles,
    dag=dag,
)

lepidoptera_email = PythonOperator(
    task_id="email",
    python_callable=lep_email.lepidoptera_email,
    dag=dag,
)

zootaxa_issues >> zootaxa_select >> zootaxa_articles
(
    [
        pensoft_articles,
        sciencedirect_articles,
        bioone_articles,
        zootaxa_articles,
        ecolmont_articles,
        fareastent_articles,
        zoonova_articles,
        biologija_articles,
        jinsbiod_articles,
        shilap_articles,
    ]
    >> merge_articles
    >> format_articles
    >> lepidoptera_email
)
merge_articles >> archive_articles
[format_articles, archive_articles] >> cleanup_articles
