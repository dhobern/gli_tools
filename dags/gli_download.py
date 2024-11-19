import os
import sys
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import gli_config as cfg
import logging
from airflow.hooks.base_hook import BaseHook



def trigger_download():

    # Define the Chrome webdriver options
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=2560,1440")
    options.add_experimental_option(
        "prefs", {"download.default_directory": cfg.coldp_path}
    )

    logging.info(f"Opening Chrome driver")

    driver = Chrome(options=options)
    driver.implicitly_wait(10)

    url = "https://sfg.taxonworks.org/"
    logging.info(f"Accessing {url}")
    driver.get(url)

    try:
        login_box = driver.find_element(By.CLASS_NAME, "box-login")

        credentials = BaseHook.get_connection("sfg_gli")

        userid = login_box.find_element(By.ID, "session_email")
        userid.send_keys(credentials.login)

        password = login_box.find_element(By.ID, "session_password")
        password.send_keys(credentials.password)

        login = login_box.find_element(By.ID, "sign_in")
        login.click()
    except:
        pass


    url = "https://sfg.taxonworks.org/projects/5/select"
    logging.info(f"Accessing {url}")
    driver.get(url)

    url = "https://sfg.taxonworks.org/tasks/exports/coldp"
    logging.info(f"Accessing {url}")
    driver.get(url)

    taxon = driver.find_element(By.ID, "otu_id_for_coldp")
    taxon.send_keys("Lepidoptera")
    field = driver.find_element(By.CLASS_NAME, "field")
    otu_select = driver.find_element(By.CLASS_NAME, "otu_tag_taxon_name")
    otu_select.click()
    download = driver.find_element(By.CLASS_NAME, "button-default")
    download.click()
    
    url = "https://sfg.taxonworks.org/downloads"
    logging.info(f"Accessing {url}")
    driver.get(url)

    updates = driver.find_element(By.CLASS_NAME, "recent_updates")
    link = updates.find_element(By.XPATH, ".//a").get_attribute('href')
    if link.startswith("/"):
        link = "https://sfg.taxonworks.org" + link

    logging.info(f"Accessing {link}")
    driver.get(link)

    sleeps = 0
    while True:
        driver.get(link)
        download_form = driver.find_element(By.CLASS_NAME, "button_to")
        download_button = download_form.find_element(By.XPATH, "./button")
        disabled = download_button.get_attribute("disabled")
        if disabled != "true":
            break
        driver.get(url)
        sleeps += 1
        logging.info(f"Sleeping {sleeps}")
        time.sleep(600)

    download_button.click()

    time.sleep(120)

    driver.close()



def download_archive():
    branch = "finish"

    try:
        trigger_download()

        branch = "unpack"
    
    except e:
        logging.info(f"Caught exception: {e}")

    return branch
