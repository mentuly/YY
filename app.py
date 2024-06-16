from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.email}')"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Product('{self.title}', '{self.author}', '{self.genre}')"

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProductForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    genre = StringField('Genre', validators=[DataRequired()])
    submit = SubmitField('Save Changes')

with app.app_context():
    db.create_all()
    if not Product.query.first():
        initial_products = [
            Product(title='Book 1', author='Author 1', genre='Fiction'),
            Product(title='Book 2', author='Author 2', genre='Non-Fiction'),
            Product(title='Book 3', author='Author 3', genre='Fantasy')
        ]
        db.session.add_all(initial_products)
        db.session.commit()

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'Logged in as {form.email.data}', 'success')
        return redirect(url_for('index'))
    return render_template('login.html', title='Login', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        user = User(email=form.email.data, password=hashed_password)
        try:
            db.session.add(user)
            db.session.commit()
            flash(f'Account created for {form.email.data}', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Error: This email is already taken. Please choose a different one.', 'danger')
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/product/new', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(title=form.title.data, author=form.author.data, genre=form.genre.data)
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully', 'success')
        return redirect(url_for('index'))
    return render_template('form_template.html', title='Add Product', form=form)

@app.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm()
    if form.validate_on_submit():
        product.title = form.title.data
        product.author = form.author.data
        product.genre = form.genre.data
        db.session.commit()
        flash('Product updated successfully', 'success')
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.title.data = product.title
        form.author.data = product.author
        form.genre.data = product.genre
    return render_template('form_template.html', title='Edit Product', form=form)

if __name__ == '__main__':
    app.run(debug=True)
