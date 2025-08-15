from ..database import get_db_connection
import requests, os, socks, socket
from bs4 import BeautifulSoup
from typing import List, Dict

# Proxy via Tor (socks5h ensures DNS via Tor)
TOR_PROXY = os.getenv('TOR_SOCKS_PROXY', 'socks5h://127.0.0.1:9050')
PROXIES = {'http': TOR_PROXY, 'https': TOR_PROXY}

def search_ahmia(wallet_address: str) -> list[dict]:
    search_url = f"https://ahmia.fi/search/?q={wallet_address}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(search_url, headers=headers, proxies=PROXIES, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        results = [
            {"title": link.text.strip(), "url": link["href"]}
            for link in soup.select(".result h4 a")
        ]
        # save even if empty
        save_darkweb_results(wallet_address, 'ahmia', results)
        return results if results else [{"title": "No results found", "url": ""}]
    except requests.RequestException as e:
        return [{"title": "Error fetching data", "url": str(e)}]
    
def search_dread(wallet_address: str) -> list[dict]:
    """
    Scrape Dread forum via Tor proxy, save results to DB, and return list.
    """
    url = (
        "http://dreadytofatroptsdj6io7l3xptbet6onoyno2yv7jicoxknyazubrad." 
        "onion/search?query=" + wallet_address
    )
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        resp = requests.get(url, headers=headers, proxies=PROXIES, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        for post in soup.find_all("div", class_="post"):
            title_tag = post.find("h3")
            link_tag = post.find("a")
            if title_tag and link_tag:
                results.append({"title": title_tag.text.strip(), "url": link_tag["href"]})
        save_darkweb_results(wallet_address, 'dread', results)
        return results if results else [{"title": "No results found", "url": ""}]
    except requests.RequestException as e:
        return [{"title": "Error fetching data", "url": str(e)}]
    
def save_darkweb_results(address: str, source: str, results: list[dict]):
    conn = get_db_connection()
    cur = conn.cursor()
    for item in results:
        cur.execute("""
            INSERT INTO darkweb_results (address, source, title, url)
            VALUES (%s, %s, %s, %s)
        """, (address, source, item['title'], item['url']))
    conn.commit()
    cur.close()
    conn.close()

def get_darkweb_results(address: str, source: str = None) -> list[dict]:
    conn = get_db_connection()
    cur = conn.cursor()
    if source:
        cur.execute(
            """
            SELECT title, url FROM darkweb_results
            WHERE address = %s AND source = %s
            ORDER BY created_at DESC
            """,
            (address, source)
        )
    else:
        cur.execute(
            """
            SELECT title, url FROM darkweb_results
            WHERE address = %s
            ORDER BY created_at DESC
            """,
            (address,)
        )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{'title': row[0], 'url': row[1]} for row in rows]
