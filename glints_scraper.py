from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import config
import sqlite3
from datetime import datetime


def run_scraper():
    conn = sqlite3.connect("vacancy.db")
    cursor = conn.cursor()

    try:
        with open("schema.sql", "r") as file_sql:
            script_sql = file_sql.read()
            cursor.executescript(script_sql)
        conn.commit()
        print("Database is ready to use by Glints")
    except FileNotFoundError:
        print("schema.sql can not be found by Glints")

    job_title = config.job_keyword
    parts = job_title.split()

    Options = webdriver.ChromeOptions()

    Options.add_argument("--headless=new")
    Options.add_argument("--disable-gpu")
    Options.add_argument("--no-sandbox")
    Options.add_argument("--window-size=1920,1080")
    Options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    Options.page_load_strategy = "eager"

    driver = webdriver.Chrome(options=Options)
    driver.get("https://glints.com/id/en")

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[placeholder='Search by Title, Skill or Company']")
        )
    ).send_keys(job_title + Keys.ENTER)

    time.sleep(10)

    jobs = WebDriverWait(driver, 5).until(
        EC.visibility_of_all_elements_located(
            (By.XPATH, "//div[@data-glints-tracking-element-name='job_card']")
        )
    )

    for job in jobs:
        try:
            title_element = job.find_element(By.XPATH, ".//a[contains(@class, 'JobCardTitle')]")
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
                    By.XPATH, ".//a[contains(@class, 'CompanyLink')]"
                )
                company = company_element.text
            except:
                company = "Nama Perusahaan Tidak Tersedia"

            print(f"Position    : {title}")
            print(f"Company     : {company}")
            print(f"Link        : {link}")
            print("Job Site    : Glints")

            now_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            cursor.execute(
                """
                INSERT OR IGNORE INTO jobs (position, company, link, job_site, date_found)
                VALUES (?, ?, ?, ?, ?)""",
                (title, company, link, "Glints", now_time),
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
