from datetime import date
from sites import justjoin
from keywords import KEYWORDS, LOCATION
from utils import save_to_csv, remove_duplicates

def run_scraper():
    all_offers = []
    total_offers_from_all_scrapers = 0
    scrapers = [("justjoin", justjoin.scrape)]

    print("Rozpoczynam proces scrapowania...")
    for name, func in scrapers:
        try:
            print(f"[{name}] Rozpoczynam scrapowanie...")
            offers = func(KEYWORDS, LOCATION)
            if offers:
                print(f"[{name}] Znaleziono {len(offers)} ofert.")
                all_offers.extend(offers)
                total_offers_from_all_scrapers += len(offers)
            else:
                print(f"[{name}] Nie znaleziono żadnych nowych ofert.")
        except Exception as e:
            # More specific exceptions (e.g., WebDriverException from Selenium)
            # could be caught here if they were consistently propagated by all scrapers.
            # For now, a general Exception catch is maintained.
            print(f"[{name}] Błąd podczas scrapowania: {e}")
            # Optionally, log the traceback for more detailed debugging
            # import traceback
            # print(traceback.format_exc())

    print(f"\nZakończono scrapowanie. Łącznie zebrano {total_offers_from_all_scrapers} ofert ze wszystkich scraperów.")

    if not all_offers:
        print("Nie zebrano żadnych ofert. Plik CSV nie zostanie utworzony/zaktualizowany.")
        return

    today_file = f"offers_{date.today().isoformat()}.csv"

    print(f"Usuwanie duplikatów i zapisywanie nowych ofert do pliku: {today_file}...")
    new_offers_after_deduplication = remove_duplicates(all_offers, today_file)

    if new_offers_after_deduplication:
        save_to_csv(new_offers_after_deduplication, today_file)
        print(f"Zapisano {len(new_offers_after_deduplication)} nowych ofert do pliku {today_file}.")
    else:
        print(f"Nie znaleziono żadnych unikalnych nowych ofert do zapisania w pliku {today_file}.")

if __name__ == "__main__":
    run_scraper()
