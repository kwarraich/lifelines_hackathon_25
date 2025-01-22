import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"
DATABASE = 'shelters.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def modify_db(query, args=()):
    conn = get_db()
    conn.execute(query, args)
    conn.commit()

@app.route('/')
def index():
    # This serves the landing page where users can choose between evacuee or shelter.
    return render_template('index.html')

@app.route('/shelter_login')
def shelter_login():
    # Redirect users to the login page designed for shelters.
    return redirect(url_for('login'))

@app.route('/evacuee_action')
def evacuee_action():
    # Placeholder for whatever action/page you want evacuees to see.
    return render_template('evacuee_page.html')  # Ensure this template is created.

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = query_db('select * from users where username = ?', [username], one=True)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['shelter_name'] = user['shelter_name']
            return redirect(url_for('manage_inventory'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        shelter_name = request.form['shelter_name']
        
        # Check if the user already exists
        if query_db('select * from users where username = ?', [username], one=True):
            return render_template('registration.html', error="Username already exists")
        
        # Hash the password and insert the new user into the database
        hashed_password = generate_password_hash(password)
        modify_db('insert into users (username, password, shelter_name) values (?, ?, ?)', [username, hashed_password, shelter_name])
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/manage_inventory', methods=['GET', 'POST'])
def manage_inventory():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    view_all = session.get('view_all', False)

    if request.method == 'POST' and not view_all:
        item_name = request.form['item_name']
        quantity = int(request.form['quantity'])

        existing_item = query_db('select * from resources where name = ? and user_id = ?', [item_name, user_id], one=True)
        if existing_item:
            modify_db('update resources set quantity = quantity + ? where id = ?', [quantity, existing_item['id']])
        else:
            modify_db('insert into resources (name, quantity, user_id) values (?, ?, ?)', [item_name, quantity, user_id])

    if view_all:
        inventory = query_db('select r.*, u.shelter_name from resources r join users u on r.user_id = u.user_id')
    else:
        inventory = query_db('select * from resources where user_id = ?', [user_id])

    return render_template('manage_inventory.html', inventory=inventory, view_all=view_all)

@app.route('/update_quantity/<int:item_id>', methods=['POST'])
def update_quantity(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    new_quantity = int(request.form['quantity'])
    modify_db('update resources set quantity = ? where id = ?', [new_quantity, item_id])
    return redirect(url_for('manage_inventory'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/toggle_view', methods=['GET'])
def toggle_view():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    view_all = session.get('view_all', False)
    session['view_all'] = not view_all
    return redirect(url_for('manage_inventory'))

if __name__ == '__main__':
    with app.app_context():
        # Ensure tables are created and the database is initialized
        db = get_db()
        db.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, shelter_name TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS resources (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, quantity INTEGER, user_id INTEGER)')
        db.commit()
    app.run(debug=True)