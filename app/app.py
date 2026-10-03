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
    # nosemgrep: python.flask.security.audit.app-run-param-config.avoid_app_run_with_bad_host
    # 0.0.0.0 qasddan: ilova Docker konteynerida ishlaydi, tashqi portga
    # EXPOSE va -p orqali ulanish uchun konteyner ichida barcha interfeyslarni
    # tinglashi SHART. Konteyner tashqarisidan izolyatsiya Docker tarmog'i
    # tomonidan ta'minlanadi. Faqat shu loyihaning demo konteksti uchun amal qiladi.
    app.run(host="0.0.0.0", port=5000)