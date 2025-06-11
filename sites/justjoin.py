import requests
from bs4 import BeautifulSoup

def scrape(keywords, location):
    url = "https://justjoin.it/all/python"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    offers = []
    for job in soup.select("a.css-4lqp8g"):
        title = job.get("title", "")
        if not any(k.lower() in title.lower() for k in keywords):
            continue
        if location.lower() not in job.text.lower():
            continue

        offers.append({
            "title": title.strip(),
            "company": job.get("data-company", "Unknown"),
            "location": location,
            "url": "https://justjoin.it" + job.get("href"),
        })

    return offers
