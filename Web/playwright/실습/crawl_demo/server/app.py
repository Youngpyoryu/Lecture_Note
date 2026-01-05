from flask import Flask, request, jsonify, session, redirect, render_template
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "demo-secret-key"  # 데모용

app.permanent_session_lifetime = timedelta(hours=2)

DEMO_EMAIL = "demo@demo.com"
DEMO_PW = "pass1234"

# 데모 데이터
ITEMS = [{"id": i, "title": f"Item {i}", "price": 1000 + i} for i in range(1, 51)]
PAGE_SIZE = 10


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/login")
def login():
    email = request.form.get("email", "")
    pw = request.form.get("password", "")
    if email == DEMO_EMAIL and pw == DEMO_PW:
        session.permanent = True
        session["user"] = email
        return redirect("/")
    return redirect("/?login=failed")


@app.post("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.get("/api/items")
def api_items():
    # 로그인 필요
    if "user" not in session:
        return jsonify({"error": "unauthorized"}), 401

    page = int(request.args.get("page", "1"))
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    data = ITEMS[start:end]
    return jsonify({
        "page": page,
        "page_size": PAGE_SIZE,
        "items": data,
        "has_next": end < len(ITEMS)
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
