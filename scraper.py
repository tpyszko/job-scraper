from datetime import date
from sites import justjoin
from keywords import KEYWORDS, LOCATION
from utils import save_to_csv, remove_duplicates

def run_scraper():
    all_offers = []
    scrapers = [("justjoin", justjoin.scrape)]

    for name, func in scrapers:
        try:
            offers = func(KEYWORDS, LOCATION)
            print(f"[{name}] Znaleziono {len(offers)} ofert.")
            all_offers.extend(offers)
        except Exception as e:
            print(f"[{name}] Błąd: {e}")

    today_file = f"offers_{date.today().isoformat()}.csv"
    new_offers = remove_duplicates(all_offers, today_file)
    save_to_csv(new_offers, today_file)

if __name__ == "__main__":
    run_scraper()
