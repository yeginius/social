from flask import Flask, send_file
from gtts import gTTS
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "사회 뉴스 속보 서버 작동 중입니다. /social 경로로 접근하세요."

@app.route("/social")
def social_news():
    titles = get_social_news_titles()
    news_text = create_announcement(titles)

    # TTS 생성 (속도 빠르게: gTTS는 속도 조정 불가 → 이후 변환 필요)
    tts = gTTS(text=news_text, lang='ko')
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

def create_announcement(titles):
    # 한국 시간 기준
    now = datetime.utcnow() + timedelta(hours=9)
    current_time = now.strftime("%H시 %M분")

    if not titles:
        return f"현재 시간 {current_time} 기준 사회 뉴스 속보가 없습니다."

    number_words = [
        "첫번째", "두번째", "세번째", "네번째", "다섯번째",
        "여섯번째", "일곱번째", "여덟번째", "아홉번째", "열번째"
    ]

    announcement = f"현재 시간 {current_time} 기준 사회 뉴스 속보 탑텐입니다. "
    for idx, title in enumerate(titles, 1):
        if idx == len(titles):
            announcement += f"마지막으로, {number_words[idx-1]} 소식, {title} 이상입니다."
        else:
            announcement += f"{number_words[idx-1]} 소식, {title}, "
    return announcement

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

