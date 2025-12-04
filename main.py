import time
import kalibrr_scraper
import glints_scraper
import jobstreet_scraper
import emailer


def main():
    try:
        kalibrr_scraper.run_scraper()
    except Exception as Error:
        print(f"Scraping error: {Error}")

    try:
        glints_scraper.run_scraper()
    except Exception as Error:
        print(f"Scraping error: {Error}")

    try:
        jobstreet_scraper.run_scraper()
    except Exception as Error:
        print(f"Scraping error: {Error}")

    time.sleep(2)

    try:
        emailer.report()
    except Exception as Error:
        print(f"Emailing error: {Error}")


if __name__ == "__main__":
    main()
