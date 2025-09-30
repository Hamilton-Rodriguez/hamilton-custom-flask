from flask import Flask, render_template

app = Flask(__name__, template_folder="templates")

@app.route("/")
def home():
    message = "Welcome to your live Flask app!"
    return render_template("index.html", message=message)

@app.route("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)


