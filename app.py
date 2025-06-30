from flask import Flask, send_file, Response
from gtts import gTTS
from datetime import datetime
import requests
from bs4 import BeautifulSoup
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
    now = datetime.now()
    current_time = now.strftime("%H시 %M분")
    
    if not titles:
        return f"<p>현재 시간 {current_time} 기준 사회 뉴스 속보가 없습니다.</p>"
    
    number_words = ["첫번째", "두번째", "세번째", "네번째", "다섯번째",
                    "여섯번째", "일곱번째", "여덟번째", "아홉번째", "열번째"]
    
    announcement = f"<p>현재 시간 {current_time} 기준 사회 뉴스 속보 탑텐입니다.</p><ol>"
    
    for idx, title in enumerate(titles, 1):
        announcement += f"<li>{number_words[idx-1]} 소식: {title}</li>"
    
    announcement += "</ol>"
    return announcement

@app.route("/social")
def social_news():
    titles = get_social_news_titles()
    news_text_html = create_announcement(titles)

    # gTTS로 음성 생성 (텍스트는 음성용 간단 버전으로)
    news_text_plain = "".join([f"{title}. " for title in titles]) or "현재 주요 사회 뉴스가 없습니다."
    tts = gTTS(text=news_text_plain, lang='ko')
    filename = "news.mp3"
    tts.save(filename)

    html_page = f"""
    <html>
    <head><meta charset="UTF-8"><title>사회 뉴스 속보</title></head>
    <body>
    {news_text_html}
    <audio controls autoplay>
      <source src="/{filename}" type="audio/mpeg">
      Your browser does not support the audio element.
    </audio>
    </body>
    </html>
    """

    return Response(html_page, mimetype='text/html')

@app.route("/news.mp3")
def serve_audio():
    return send_file("news.mp3", mimetype="audio/mpeg")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
