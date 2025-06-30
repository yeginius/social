from flask import Flask, send_file, request
from datetime import datetime
from gtts import gTTS
from bs4 import BeautifulSoup
import requests
import os
import shutil

app = Flask(__name__)

@app.route("/")
def home():
    return "사회 뉴스 속보 서버 작동 중입니다. /social 경로를 확인해보세요."

@app.route("/social")
def social_news():
    now = datetime.now().strftime("%Y%m%d%H")
    filename = f"news_{now}.mp3"
    static_path = os.path.join("static", filename)

    titles = get_social_news_titles()
    news_text = create_announcement(titles)

    # mp3 파일이 없으면 생성
    if not os.path.exists(static_path):
        tts = gTTS(text=news_text, lang='ko')
        if not os.path.exists("static"):
            os.mkdir("static")
        tts.save(static_path)

    # HTML 응답 반환 (텍스트 + 오디오 자동 재생)
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>사회 뉴스 속보</title>
    </head>
    <body>
        <h2>사회 뉴스 속보</h2>
        <p>{news_text}</p>
        <audio controls autoplay>
            <source src="/static/{filename}" type="audio/mpeg">
            브라우저가 오디오를 지원하지 않습니다.
        </audio>
    </body>
    </html>
    """
    return html

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
