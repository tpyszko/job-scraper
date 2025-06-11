import csv
import os
import pandas as pd

def save_to_csv(offers, filename):
    if not offers:
        print("Brak nowych ofert.")
        return
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=offers[0].keys())
        writer.writeheader()
        writer.writerows(offers)

def remove_duplicates(new_offers, csv_path):
    if not os.path.exists(csv_path):
        return new_offers
    old_df = pd.read_csv(csv_path)
    old_urls = set(old_df['url'])
    return [offer for offer in new_offers if offer['url'] not in old_urls]
