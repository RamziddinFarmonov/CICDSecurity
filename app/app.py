
# VAQTINCHALIK TEST — GitLeaks buni ushlashi kerak
AWS_SECRET_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE7wJalrXUtnFEMI/K7MDENG/bPxRfiCY"

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