from flask import Flask, send_file
import requests
from bs4 import BeautifulSoup
from gtts import gTTS
from datetime import datetime

app = Flask(__name__)

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
    now = datetime.now()
    current_time = now.strftime("%H시 %M분")

    if not titles:
        return f"현재 시간 {current_time} 기준 사회 뉴스 속보가 없습니다."

    number_words = ["첫번째", "두번째", "세번째", "네번째", "다섯번째",
                    "여섯번째", "일곱번째", "여덟번째", "아홉번째", "열번째"]

    announcement = f"현재 시간 {current_time} 기준 사회 뉴스 속보 탑텐입니다. "

    for idx, title in enumerate(titles, 1):
        if idx == len(titles):
            announcement += f"마지막으로, {number_words[idx - 1]} 소식, {title} 이상입니다."
        else:
            announcement += f"{number_words[idx - 1]} 소식, {title}, "

    return announcement

@app.route("/social")
def social_news():
    titles = get_social_news_titles()
    text = create_announcement(titles)

    tts = gTTS(text=text, lang='ko')
    mp3_path = "news.mp3"
    tts.save(mp3_path)

    return send_file(mp3_path, mimetype="audio/mpeg")

@app.route("/")
def home():
    return "사회 뉴스 속보 서버 작동 중입니다. /social 경로로 접속하세요."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
