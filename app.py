from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
import feedparser
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Laad .env met db-config
load_dotenv()
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_RSS'),
    'port': int(os.getenv('DB_PORT', 3306))
}

# zet een database connectie op vanuit hetS config bestand
def get_db_connection():
    return mysql.connector.connect(**db_config)

def get_all_feeds():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT title, url, category FROM rss_feeds")
    all_feeds = cursor.fetchall()
    cursor.close()
    connection.close()
    return all_feeds

def get_feeds_for_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT f.*
        FROM rss_feeds f
        JOIN user_feeds uf ON f.id = uf.feed_id
        WHERE uf.user_id = %s
    """, (user_id,))
    feeds = cursor.fetchall()
    cursor.close()
    connection.close()
    return feeds

@app.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT rf.*
        FROM rss_feeds rf
        JOIN user_feeds uf ON rf.id = uf.feed_id
        WHERE uf.user_id = %s
    """, (session['user_id'],))
    feeds = cursor.fetchall()
    cursor.close()
    connection.close()

    categories = {}
    for feed in feeds:
        parsed = feedparser.parse(feed["url"])
        if parsed.bozo:
            continue

        category = feed["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append({
            "title": feed["title"],
            "items": parsed.entries[:5]
        })
    # Alle bestaande feeds (voor dropdown)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT title, url, category FROM rss_feeds")
    all_feeds = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("dashboard.html", categories=categories, username=session.get('username'),
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), all_feeds=all_feeds)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed = generate_password_hash(password)

        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed))
            connection.commit()
        except mysql.connector.errors.IntegrityError:
            return "Gebruiker bestaat al", 400
        finally:
            cursor.close()
            connection.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user and check_password_hash(user['password_hash'], password):
            session['username'] = user['username']
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        return "Ongeldige inloggegevens", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/add_feed', methods=['POST'])
def add_feed():
    if 'user_id' not in session:
        return redirect('/login')

    existing = request.form.get('existing')
    user_id = session['user_id']

    if existing:
        # uit dropdown geselecteerd
        title, url, category = existing.split('|')
    else:
        title = request.form['title']
        url = request.form['url']
        category = request.form['category']

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    # Check of feed al bestaat
    cursor.execute("SELECT id FROM rss_feeds WHERE url = %s", (url,))
    feed = cursor.fetchone()

    if not feed:
        # Voeg nieuwe feed toe
        cursor.execute(
            "INSERT INTO rss_feeds (title, url, category, user_id) VALUES (%s, %s, %s, %s)",
            (title, url, category, user_id)
        )
        connection.commit()
        feed_id = cursor.lastrowid
    else:
        feed_id = feed['id']

    # Check of feed al gekoppeld is aan deze gebruiker
    cursor.execute("SELECT * FROM user_feeds WHERE user_id = %s AND feed_id = %s", (user_id, feed_id))
    exists = cursor.fetchone()
    if not exists:
        # Voeg koppeling toe
        cursor.execute("INSERT INTO user_feeds (user_id, feed_id) VALUES (%s, %s)", (user_id, feed_id))
        connection.commit()

    cursor.close()
    connection.close()

    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
