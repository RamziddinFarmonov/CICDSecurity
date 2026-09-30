import os
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify(message="CI/CD Security Demo", status="ok")


@app.route("/health")
def health():
    return jsonify(status="healthy")


@app.route("/ping")
def ping():
    # VAQTINCHALIK TEST — Semgrep buni ushlashi kerak (command injection)
    host = request.args.get("host", "localhost")
    result = os.system("ping -c 1 " + host)
    return jsonify(result=result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)