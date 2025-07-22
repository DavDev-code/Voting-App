from flask import Flask, render_template, request, redirect, url_for, make_response
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('poll.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS choices(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        genre TEXT NOT NULL,
        votes INTEGER DEFAULT 0
    )''')
    c.execute('SELECT COUNT(*) FROM choices')
    if c.fetchone()[0] == 0:
        genres = ['Stealth', 'Roguelike', 'Turn-Based', 'Immersive Sim', 'Hack and Slash', 'Platformer', 'Metroidvania', 'Action Adventure', 'Rhythm']
        c.executemany('INSERT INTO choices(genre, votes) VALUES(?, 0)', [(glossa,) for glossa in genres])
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect('poll.db')
    c = conn.cursor()
    has_voted = request.cookies.get('has_voted')

    if request.method == 'POST':
        if has_voted:
            conn.close()
            return redirect(url_for('results'))

        choice_id = request.form.get('genre')
        if choice_id:
            c.execute('UPDATE choices SET votes = votes + 1 WHERE id = ?', (choice_id,))
            conn.commit()
            response = make_response(redirect(url_for('results')))
            response.set_cookie('has_voted', 'true')
            conn.close()
            return response

    c.execute('SELECT id, genre FROM choices')
    choices = c.fetchall()
    conn.close()
    return render_template('index.html', choices=choices)

@app.route('/results')
def results():
    conn = sqlite3.connect('poll.db')
    c = conn.cursor()
    c.execute('SELECT genre, votes FROM choices ORDER BY votes DESC')
    results = c.fetchall()
    conn.close()
    return render_template('results.html', results=results)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
