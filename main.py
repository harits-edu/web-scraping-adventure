import time
import scraper
import emailer

def main():
    try:
        scraper.run_scraper()
    except Exception as Error:
        print(f"Scraping error: {Error}")
    
    time.sleep(2)

    try:
        emailer.report()
    except Exception as Error:
        print(f"Emailing error: {Error}")

if __name__ == "__main__":
    main()