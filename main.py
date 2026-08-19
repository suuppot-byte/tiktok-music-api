from fastapi import FastAPI, HTTPException, Query
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin

app = FastAPI(title="TikTok Music API")

SEARCH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36"
}

TIKWM_HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.8",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://tikwm.com",
    "referer": "https://tikwm.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}

def search_urlebird(text: str):
    url = "https://urlebird.com/search/?q=" + quote(text)
    try:
        response = requests.get(url, headers=SEARCH_HEADERS, timeout=20)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/video/" in href:
                return urljoin("https://urlebird.com", href)
        return None
    except Exception:
        return None

def get_tikwm_data(tiktok_link: str):
    try:
        response = requests.post(
            "https://tikwm.com/api/",
            headers=TIKWM_HEADERS,
            data={"url": tiktok_link, "hd": "1"},
            timeout=20
        )
        result = response.json()
        if result.get("code") != 0:
            return None
        return result.get("data", {})
    except Exception:
        return None

@app.get("/tiktok")
def search_tiktok(q: str = Query(..., description="كلمة البحث عن المقطع أو الصوت")):
    tiktok_link = search_urlebird(q)
    if not tiktok_link:
        raise HTTPException(status_code=404, detail={"error": "❌ ماكو فيديو"})
    
    data = get_tikwm_data(tiktok_link)
    if not data:
        raise HTTPException(status_code=500, detail={"error": "❌ فشل جلب البيانات"})
    
    return {
        "status": "success",
        "query": q,
        "video_url": tiktok_link,
        "title": data.get("title", "No Title"),
        "music_url": data.get("music_info", {}).get("play")
    }
