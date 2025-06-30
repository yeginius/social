from flask import Flask, send_file
from gtts import gTTS
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route("/social")
def social_news():
    titles = get_social_news_titles()
    now = datetime.utcnow() + timedelta(hours=9)
    current_time = now.strftime("%H시 %M분")

    number_words = [
        "첫번째", "두번째", "세번째", "네번째", "다섯번째",
        "여섯번째", "일곱번째", "여덟번째", "아홉번째", "열번째"
    ]

    if not titles:
        news_text = f"현재 시간 {current_time} 기준 사회 뉴스 속보가 없습니다."
    else:
        news_text = f"현재 시간 {current_time} 기준 사회 뉴스 속보 탑텐입니다. "
        for idx, title in enumerate(titles, 1):
            if idx == len(titles):
                news_text += f"마지막으로, {number_words[idx-1]} 소식, {title} 이상입니다."
            else:
                news_text += f"{number_words[idx-1]} 소식, {title}, "

    # gTTS 음성 생성
    tts = gTTS(text=news_text.strip(), lang='ko')
    filename = "news.mp3"
    tts.save(filename)

    return send_file(filename, mimetype="audio/mpeg")

def get_social_news_titles(max_count=10):
    url = "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=102"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    articles = soup.select("ul.type06_headline li dt:not(.photo) a")
    titles = []
    for article in articles:
        title = article.get_text(strip=True)
        if title not in titles:
            titles.append(title)
        if len(titles) == max_count:
            break
    return titles

@app.route("/")
def home():
    return "사회 뉴스 속보 서버 작동 중입니다. '/social'로 접속 시 음성 뉴스가 재생됩니다."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
