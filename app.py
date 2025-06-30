from flask import Flask, send_file
from gtts import gTTS
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from pydub import AudioSegment
import os

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
    now = datetime.utcnow() + timedelta(hours=9)  # 한국 시간으로 맞춤
    current_time = now.strftime("%H시 %M분")
    
    if not titles:
        return f"현재 시간 {current_time} 기준 사회 뉴스 속보가 없습니다."
    
    number_words = ["첫번째", "두번째", "세번째", "네번째", "다섯번째",
                    "여섯번째", "일곱번째", "여덟번째", "아홉번째", "열번째"]
    
    announcement = f"현재 시간 {current_time} 기준 사회 뉴스 속보 탑텐입니다. "
    
    for idx, title in enumerate(titles, 1):
        if idx == len(titles):
            announcement += f"마지막으로, {number_words[idx-1]} 소식, {title} 이상입니다."
        else:
            announcement += f"{number_words[idx-1]} 소식, {title}, "
    return announcement

@app.route("/social")
def social_news():
    titles = get_social_news_titles()
    news_text = create_announcement(titles)

    # gTTS로 음성 생성
    tts = gTTS(text=news_text, lang='ko')
    raw_path = "/tmp/news_raw.mp3"
    final_path = "/tmp/news.mp3"
    tts.save(raw_path)

    # pydub로 음성 속도 1.25배 빠르게 조정
    sound = AudioSegment.from_file(raw_path)
    faster_sound = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * 1.25)
    }).set_frame_rate(sound.frame_rate)
    faster_sound.export(final_path, format="mp3")

    # 음성 파일 보내기 (mp3)
    return send_file(final_path, mimetype="audio/mpeg")

@app.route("/")
def home():
    return "사회 뉴스 속보 서버 작동 중입니다. /social 경로로 접속하세요."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
