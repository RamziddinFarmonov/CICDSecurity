import subprocess
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
    host = request.args.get("host", "localhost")
    result = subprocess.run(
        ["ping", "-c", "1", host],
        capture_output=True,
        text=True,
        timeout=5,
    )
    return jsonify(output=result.stdout)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)