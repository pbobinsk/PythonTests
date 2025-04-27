from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

@app.before_request
def create_tables():
    # Stworzy tabele jeśli ich nie ma
    db.create_all()

# Strona główna
@app.route('/')
def index():
    return render_template('index.html')

# Lista użytkowników
@app.route('/users')
def list_users():
    users = User.query.all()
    return render_template('user_list.html', users=users)

# Dodawanie użytkownika
@app.route('/users/new', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        new_user = User(name=name, email=email)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('list_users'))
    return render_template('user_form.html')

# Edycja użytkownika
@app.route('/users/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        db.session.commit()
        return redirect(url_for('list_users'))
    return render_template('user_form.html', user=user)

# Usuwanie użytkownika
@app.route('/users/delete/<int:id>')
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('list_users'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
