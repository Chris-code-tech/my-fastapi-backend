import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter

router = APIRouter()


def scrape_healthline_articles():
    url = "https://www.healthline.com/health"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    articles = []
    print(soup.prettify())

    for item in soup.select("a.css-1wx75fd"):
        title = item.get_text(strip=True)
        link = "https://www.healthline.com" + item.get("href")
        if title and link:
            articles.append({"title": title, "link": link})

    return {"articles": articles}


@router.get("/home")
def get_home_articles():
    return scrape_healthline_articles()
