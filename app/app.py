
# VAQTINCHALIK TEST — GitLeaks buni ushlashi kerak
AWS_ACCESS_KEY_ID = "AKIAZ7XKMN2P4R8QW1T5"
AWS_SECRET_ACCESS_KEY = "kR9mLpQz3XvT7bNwYc1FdGhJs5AeUi8OqWr2ZnMx"

from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify(message="CI/CD Security Demo", status="ok")


@app.route("/health")
def health():
    return jsonify(status="healthy")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)