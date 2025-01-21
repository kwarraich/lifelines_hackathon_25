from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Shelter, Resource

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shelters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "supersecretkey"  # Needed for session management

db.init_app(app)

# Home route redirects to login
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        shelter_name = request.form.get('shelter_name')

        if not username or not password or not shelter_name:
            return render_template('register.html', error="All fields are required.")

        with app.app_context():
            # Check if the shelter already exists
            shelter = Shelter.query.filter_by(name=shelter_name).first()
            if not shelter:
                shelter = Shelter(name=shelter_name)
                db.session.add(shelter)
                db.session.commit()

            # Check if the username is already taken
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return render_template('register.html', error="Username already exists. Choose another.")

            # Create a new user linked to the shelter
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password, shelter_id=shelter.id)
            db.session.add(new_user)
            db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with app.app_context():
            user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['shelter_id'] = user.shelter_id  # Store shelter_id in session
            session['username'] = user.username
            return redirect(url_for('manage_inventory'))  # Redirect to inventory after login
        else:
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

# Manage inventory route (shelter-specific)
@app.route('/manage_inventory', methods=['GET', 'POST'])
def manage_inventory():
    if 'shelter_id' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    shelter_id = session['shelter_id']  # Get the logged-in shelter ID

    if request.method == 'POST':
        item_name = request.form['item_name']
        quantity = int(request.form['quantity'])

        with app.app_context():
            existing_item = Resource.query.filter_by(name=item_name, shelter_id=shelter_id).first()

        if existing_item:
            existing_item.quantity += quantity  # Update quantity
        else:
            new_item = Resource(name=item_name, quantity=quantity, shelter_id=shelter_id)
            db.session.add(new_item)

        db.session.commit()

    # Fetch only resources that belong to the logged-in shelter
    with app.app_context():
        inventory = Resource.query.filter_by(shelter_id=shelter_id).all()
    
    return render_template('manage_inventory.html', inventory=inventory)

# Route to update inventory item quantity
@app.route('/update_quantity/<int:item_id>', methods=['POST'])
def update_quantity(item_id):
    if 'shelter_id' not in session:
        return redirect(url_for('login'))

    new_quantity = int(request.form['quantity'])
    
    with app.app_context():
        item = Resource.query.filter_by(id=item_id, shelter_id=session['shelter_id']).first()
        if item:
            item.quantity = new_quantity
            db.session.commit()

    return redirect(url_for('manage_inventory'))

# Welcome page after login
@app.route('/welcome')
def welcome():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('welcome.html', username=session['username'])

# Logout route
@app.route('/logout')
def logout():
    session.clear()  # Clears session data
    return redirect(url_for('login'))

# Initialize database
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables exist before running the app
    app.run(debug=True)
