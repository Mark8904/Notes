from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import secrets

app = Flask(__name__, template_folder='templates')
app.secret_key = secrets.token_hex(16)  # Generate a random secret key

# Create a simple SQLite database for users
def connect_to_database():
    return sqlite3.connect('users.db')

def create_user_table(user):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {user} (title TEXT, content TEXT)")
    conn.commit()
    conn.close()

def create_users_table():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (name TEXT, id TEXT)''')
    conn.commit()
    conn.close()


create_users_table()


@app.route('/')
def login():
    return render_template('index.html')


@app.route('/auth', methods=['POST'])
def auth():
    name = request.form['Name']
    iden = request.form['Password']
    try:
        with connect_to_database() as conn:
            cursor = conn.cursor()
            # Check if the user exists in the database
            cursor.execute('SELECT * FROM users WHERE name = ? AND id = ?', (name, iden))
            user = cursor.fetchone()

        if user:
            # Store user data in session
            session['Name'] = name
            create_user_table(name)
            return redirect('/dashboard')

        else:
            return render_template('index.html', message='Invalid login credentials.')

    except sqlite3.Error as e:
        # Handle database errors
        print("Database error:", e)
        return render_template('index.html', message='An error occurred while processing your request.')
    
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'Name' in session:
        name = session['Name']
        if request.method == 'POST':
            title = request.form["Title"]
            content = request.form["Content"]
            save_note_to_database(name, title, content)
        titles = get_user_titles(name)
        return render_template('dashboard.html', titles=titles,name=name)
    return redirect('/')

def get_user_titles(user):
    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT title FROM {user}")
        rows = cursor.fetchall()
        titles = [row[0] for row in rows]  # Extracting titles from rows
        return titles
    except sqlite3.Error as e:
        print("Error fetching titles from database:", e)
        return []
    finally:
        conn.close()


def save_note_to_database(user, title, content):
    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        sql_statement = f"INSERT INTO {user} VALUES (?, ?)"
        cursor.execute(sql_statement, (title, content))
        conn.commit()
        print("Note saved successfully.")
    except sqlite3.Error as e:
        print("Error saving note to database:", e)
    finally:
        conn.close()

@app.route('/ntr',methods=['GET','POST'])
def nt():
    return render_template('notes.html')
    

@app.route('/note', methods=['GET'])
def get_note():
    title = request.args.get('title', '')
    if 'Name' in session:
        name = session['Name']
        content = get_note_content(name, title)
        return content
    return jsonify({'error': 'User not logged in'}), 403

def get_note_content(user, title):
    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT content FROM {user} WHERE title = ?", (title,))
        row = cursor.fetchone()
        if row:
            return row[0]
        else:
            return "Note not found."
    except sqlite3.Error as e:
        print("Error fetching note content from database:", e)
        return "Error fetching note content."
    finally:
        conn.close()
    
@app.route('/registerate', methods=['GET','POST'])
def reg():
    return render_template('registration.html')

@app.route('/auth1', methods=['GET','POST'])
def register():
    name = request.form['Name']
    iden = request.form['Password']
    den  = request.form['SPassword']
    if(iden==den):
        try:
            with connect_to_database() as conn:
                cursor = conn.cursor()
                # Check if the user already exists
                cursor.execute('SELECT * FROM users WHERE name = ?', (name,))
                existing_user = cursor.fetchone()
                if existing_user:
                    return render_template('registration.html',message='Username Already Exists!')

                # Insert new user into the database
                else:
                 cursor.execute('INSERT INTO users (name, id) VALUES (?, ?)', (name, iden))
                 conn.commit()
                 return render_template('registration.html',message='Succesfully Registered!')
                
        
        except sqlite3.Error as e:
            # Handle database errors
            print("Database error:", e)
            return render_template('registration.html', message='An error occurred while processing your request.')
    else:
        return render_template('registration.html',message='Enter Password Correctly!')

# Update Note Route
@app.route('/update', methods=['POST'])
def update_note():
    if 'Name' in session:
        name = session['Name']
        title = request.form['Title']
        content = request.form['Content']
        update_note_in_database(name, title, content)
        return redirect('/dashboard')  # Redirect to dashboard after successful update
    return redirect('/login')  # Redirect to login page if user is not logged in

def update_note_in_database(user, title, content):
    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        cursor.execute(f"UPDATE {user} SET content = ? WHERE title = ?", (content, title))
        conn.commit()
        print("Note updated successfully.")
    except sqlite3.Error as e:
        print("Error updating note in database:", e)
    finally:
        conn.close()


# Delete Note Route
@app.route('/delete', methods=['DELETE'])
def delete_note():
    title = request.args.get('title', '')
    if 'Name' in session:
        name = session['Name']
        delete_note_from_database(name, title)
        return 'Note deleted successfully', 200
    return jsonify({'error': 'User not logged in'}), 403

def delete_note_from_database(user, title):
    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        cursor.execute(f"DELETE FROM {user} WHERE title = ?", (title,))
        conn.commit()
        print("Note deleted successfully.")
    except sqlite3.Error as e:
        print("Error deleting note from database:", e)
    finally:
        conn.close()

# Search Notes Route
@app.route('/search', methods=['GET'])
def search_notes():
    term = request.args.get('term', '')
    if 'Name' in session:
        name = session['Name']
        search_results = search_notes_in_database(name, term)
        return render_template('search_results.html', results=search_results)
    return redirect('/')

def search_notes_in_database(user, term):
    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT title FROM {user} WHERE title LIKE ?", ('%' + term + '%',))
        rows = cursor.fetchall()
        titles = [row[0] for row in rows]
        return titles
    except sqlite3.Error as e:
        print("Error searching notes in database:", e)
        return []
    finally:
        conn.close()


@app.route('/logout')
def logout():
    # Remove user data from session
    session.pop('Name', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
