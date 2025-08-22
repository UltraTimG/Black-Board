from flask import Flask, request, redirect, session, render_template, flash
import sqlite3
from ai import ask_query
import sqlalchemy

app = Flask(__name__)
app.secret_key = 'anythingreally'

@app.route('/', methods=['GET', 'POST'])
def index():
    ai_response = None
    event_msg = None

    # Handle AI query
    if request.method == 'POST' and 'user_query' in request.form:
        user_query = request.form.get('user_query')
        if user_query:
            ai_response = ask_query(user_query)

    return render_template('index.html', ai_response=ai_response, event_msg=event_msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    username = request.form.get('username')
    password = request.form.get('password')

    connection = sqlite3.connect('blackboard.db')
    cursor = connection.cursor()
    user = cursor.execute('SELECT * FROM user WHERE username = ? AND password = ?', (username, password))
    user = user.fetchone()
    
    if user is not None:
        session['user'] = user[1]
        return render_template('index.html')
    else:
        return render_template('login.html', msg='Invalid username or password')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    connection = sqlite3.connect('blackboard.db')
    cursor = connection.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS user (id integer PRIMARY KEY, username VARCHAR(255), password VARCHAR(225))')

    username = request.form.get('username')
    password = request.form.get('password')

    if username and password:
        cursor.execute('INSERT INTO user (username, password) VALUES (?, ?)', (username, password))
        connection.commit()
        flash('Registration successful. Please log in.', 'success')
        return render_template('login.html')
    else:
        flash('Please enter both username and password.', 'error')
        return render_template('register.html')
    
@app.route('/view_calendar')
def view_calendar():
    if 'user' not in session:
        return redirect('/login')
    connection = sqlite3.connect('blackboard.db')
    cursor = connection.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, username VARCHAR(255), event TEXT)')
    cursor.execute('SELECT event FROM events WHERE username = ?', (session['user'],))
    events = [row[0] for row in cursor.fetchall()]
    connection.close()
    return render_template('view_calendar.html', events=events)

@app.route('/ask_ai', methods=['POST'])
def ask_ai():
    '''Handle AI query from the form'''
    query = request.form.get('user_query')
    system_prompt = 'return the answer to the question in html format. Do not include any other text.' \
    'The response will be displayed in a section of an already existing html page. so it should not include the' \
    'html and body tags. a div or a section is okay.' \
    
    # Call the AI function to get the response
    if query:
        final_prompt = f'{system_prompt} -- {query}'
        response = ask_query(final_prompt)
        return render_template('index.html', ai_response=response)


if __name__ == '__main__':
    app.run(debug=True)