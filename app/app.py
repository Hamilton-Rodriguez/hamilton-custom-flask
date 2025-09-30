from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import os
import re
import requests

from dotenv import load_dotenv

load_dotenv()  # loads .env if present

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASS = os.getenv("DB_PASS", "")
DB_NAME = os.getenv("DB_NAME", "kv_store")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "change-me-for-prod")

ALNUM_RE = re.compile(r'^[A-Za-z0-9]+$')

def get_db_conn():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=DB_PORT,
        autocommit=True
    )

def get_instance_dns():
    # Try EC2 metadata public-hostname. Timeout short so it fails fast off-EC2.
    try:
        r = requests.get("http://169.254.169.254/latest/meta-data/public-hostname", timeout=0.5)
        if r.status_code == 200 and r.text:
            return r.text
    except Exception:
        pass
    # fallback to hostname
    try:
        import socket
        return socket.getfqdn()
    except Exception:
        return "unknown-host"

@app.route("/")
def index():
    dns = get_instance_dns()
    # Read rows
    rows = []
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, `key`, `value` FROM kv ORDER BY id ASC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        flash("Failed to read database: " + str(e), "danger")
    return render_template("index.html", rows=rows, dns=dns)

@app.route("/insert", methods=["POST"])
def insert():
    key = request.form.get("key", "").strip()
    value = request.form.get("value", "").strip()

    if not key or not value:
        flash("Key and value are required", "warning")
        return redirect(url_for("index"))

    if not ALNUM_RE.match(key) or not ALNUM_RE.match(value):
        flash("Only alphanumeric characters allowed for key and value", "warning")
        return redirect(url_for("index"))

    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO kv (`key`, `value`) VALUES (%s, %s)", (key, value))
        cur.close()
        conn.close()
        flash("Inserted successfully", "success")
    except mysql.connector.Error as err:
        flash("Database error: " + str(err), "danger")
    except Exception as e:
        flash("Error: " + str(e), "danger")
    return redirect(url_for("index"))

@app.route("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
