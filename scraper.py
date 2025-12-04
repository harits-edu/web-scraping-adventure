# [] - Haritsyam Anshari, harits-edu - []
# [] - web-scraping-adventure project - []

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import config
import sqlite3

def run_scraper():
    conn = sqlite3.connect("vacancy.db")
    cursor = conn.cursor()

    try:
        with open("schema.sql", "r") as file_sql:
            script_sql = file_sql.read()
            cursor.executescript(script_sql)
        conn.commit()
        print("Database is ready to use")
    except FileNotFoundError:
        print("schema.sql can not be found")

    job_title = config.job_keyword
    parts = job_title.split()

    Options = webdriver.ChromeOptions()

    Options.add_argument("--headless=new") 
    Options.add_argument("--disable-gpu") 
    Options.add_argument("--no-sandbox") 
    Options.add_argument("--window-size=1920,1080")
    Options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=Options)
    driver.get("https://www.kalibrr.id/id-ID/home/co/Indonesia")

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[placeholder='Job Position']")
        )
    ).send_keys(job_title + Keys.ENTER)

    time.sleep(10)

    jobs = WebDriverWait(driver, 5).until(
        EC.visibility_of_all_elements_located((By.XPATH, "//div[h2/a[@itemprop='name']]"))
    )

    for job in jobs:
        try:
            title_element = job.find_element(By.XPATH, ".//a[@itemprop='name']")
            title = title_element.text
        except:
            continue

        is_match = True

        for word in parts:
            pattern = re.escape(word)

            if not re.search(pattern, title, re.IGNORECASE):
                is_match = False
                break

        if is_match:
            link = title_element.get_attribute("href")

            try:
                company_element = job.find_element(
                    By.XPATH, ".//a[contains(@href, 'action=Company')]"
                )
                company = company_element.text
            except:
                company = "Nama Perusahaan Tidak Tersedia"

            print(f"Position    : {title}")
            print(f"Company     : {company}")
            print(f"Link        : {link}")

            cursor.execute(
                """
                INSERT OR IGNORE INTO jobs (position, company, link)
                VALUES (?, ?, ?)""",
                (title, company, link),
            )

            if cursor.rowcount > 0:
                print("[New] - Data inserted into database")
            else:
                print("[Old] - Data already available on database")

            conn.commit()
            print("-*" * 30)

    driver.quit()
    conn.close()

if __name__ == "__main__":
    run_scraper()
