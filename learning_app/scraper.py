import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

SOURCES = [
    {
        "name": "Wikipedia",
        "url": "https://en.wikipedia.org/wiki/{query}",
        "content_selector": "div#mw-content-text p",
    },
    {
        "name": "GeeksForGeeks",
        "url": "https://www.geeksforgeeks.org/{query}/",
        "content_selector": "div.article-body p",
    },
]


def _clean(text):
    return " ".join(text.split())


def scrape_wikipedia(topic):
    query = topic.strip().replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/{query}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return None, url
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.select("div#mw-content-text p")
        text = "\n\n".join(
            _clean(p.get_text()) for p in paragraphs if len(p.get_text(strip=True)) > 40
        )
        return text or None, url
    except requests.RequestException:
        return None, url


def scrape_geeksforgeeks(topic):
    query = topic.strip().lower().replace(" ", "-")
    url = f"https://www.geeksforgeeks.org/{query}/"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return None, url
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.select("div.article-body p")
        text = "\n\n".join(
            _clean(p.get_text()) for p in paragraphs if len(p.get_text(strip=True)) > 40
        )
        return text or None, url
    except requests.RequestException:
        return None, url


def fetch_topic(topic):
    """Try Wikipedia first, fall back to GeeksForGeeks."""
    content, url = scrape_wikipedia(topic)
    if content:
        return content, url

    content, url = scrape_geeksforgeeks(topic)
    if content:
        return content, url

    return None, None
