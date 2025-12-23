# app.py
from flask import Flask

app = Flask(__name__)  # Flask 객체 생성


@app.route("/")
def index():
    return "<h1>Hello World!</h1>"


if __name__ == "__main__":  # 모듈이 직접 실행될 때만 서버 실행
    app.run(debug=True, port=5000)  # debug/port 설정 가능
