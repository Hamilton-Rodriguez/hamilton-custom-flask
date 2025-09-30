from flask import Flask, render_template
import requests

app = Flask(__name__, template_folder="templates")

def get_dns():
    try:
        r = requests.get("http://169.254.169.254/latest/meta-data/public-hostname", timeout=0.5)
        return r.text if r.ok else "unknown"
    except:
        return "unknown"

@app.route("/")
def home():
    message = "Welcome to your live Flask app!"
    dns_name = get_dns()
    return render_template("index.html", message=message, dns=dns_name)

@app.route("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)

