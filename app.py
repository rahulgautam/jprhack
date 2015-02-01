import os
import datetime
from flask import Flask, redirect, url_for, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin, login_user, logout_user,\
    current_user
from oauth import OAuthSignIn
import flask.ext.restless
from flask.ext.rqify import init_rqify

# Facebook App BAE

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '1399369633698495',
        'secret': '1b99ae7f1b81cc8d72666402a1444a14'
    },
    'twitter': {
        'id': '3RzWQclolxWZIMq5LJqzRZPTl',
        'secret': 'm9TEd58DSEtRrZHpz2EjrV9AhsBRxKMo8m3kuIZj3zLwzwIimt'
    }
}

init_rqify(app)

db = SQLAlchemy(app)
lm = LoginManager(app)
#lm.login_view = 'index'


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    profile_url = db.Column(db.String(1000), nullable=True)
    name = db.Column(db.String(200), nullable=True)
    gender = db.Column(db.String(1000), nullable=True)

    # def __init__(social_id,
    #         nickname,
    #         email,
    #         first_name,
    #         last_name,
    #         profile_url,
    #         name,
    #         gender):
    #     self.social_id = social_id
    #     self.nickname = nickname
    #     self.email = email
    #     self.first_name = first_name
    #     self.last_name = last_name
    #     self.profile_url = profile_url
    #     self.name = name
    #     self.gender = gender

post_products = db.Table('post_products',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", uselist=False, backref=db.backref("posts", lazy='dynamic'))
    category = db.Column(db.String(64), nullable=False)
    difficulty = db.Column(db.String(64), nullable=False)
    effort = db.Column(db.String(64), nullable=False)
    post_image = db.Column(db.String(64), default="")
    heading = db.Column(db.String(64), nullable=False)
    tagline = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    serve = db.Column(db.String(64), nullable=False)
    prep_time = db.Column(db.Integer, nullable=False)
    cook_time = db.Column(db.Integer, nullable=False)
    total_time = db.Column(db.Integer, nullable=False)
    ingredients = db.Column(db.String, nullable=False) #Splited by #$IN$
    directions = db.Column(db.String, nullable=False)  #Splited by #$DI$
    likes = db.Column(db.Integer, default=1)
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime, default=db.func.now())
    products = db.relationship('Product', uselist=True, secondary=post_products, backref=db.backref('posts', lazy='dynamic'))

    def __init__(self,
                user_id = None,
                category = None, 
                difficulty = None, 
                effort = None, 
                heading = None,
                post_image = None, 
                tagline = None, 
                description = None, 
                serve = None, 
                prep_time = None, 
                cook_time = None,
                ingredients = None,
                directions = None):
        self.user_id = 1 #current_user.id
        self.category = category
        self.difficulty = difficulty
        self.effort = effort
        self.heading = heading
        self.post_image = post_image
        self.tagline = tagline
        self.description = description
        self.serve = serve
        self.prep_time = prep_time
        self.cook_time = cook_time
        self.total_time = prep_time + cook_time
        self.update_on = datetime.datetime.utcnow()
        self.ingredients = ingredients
        self.directions = directions


class Product(db.Model):
    """docstring for Product"""
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.String(10), nullable=False) 
    vendor = db.Column(db.Integer, nullable=False) 
    measure = db.Column(db.String(40), nullable=False)
    price = db.Column(db.Integer, nullable=False) 

    def __init__(self, name, quantity, vendor, measure, price):
        self.name = name
        self.quantity = quantity
        self.vendor = vendor
        self.measure = measure
        self.price = price


class Vendor(db.Model):
    """docstring for Vendor"""
    __tablename__ = "vendor"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(1000), nullable=False) 
    email = db.Column(db.Integer, nullable=False) 
    phone = db.Column(db.String(40), nullable=False) 

    def __init__(self, name, address, email, phone):
        self.name = name
        self.address = name
        self.email = name
        self.phone = name


class Order(db.Model):
    """docstring for Order"""
    __tablename__ = "order"
    id  = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    placed_on = db.Column(db.DateTime)
    deliverd_on = db.Column(db.DateTime)

    def __init__(self, id, user_id, placed_on, deliverd_on):
        self.id = id
        self.user_id = user_id
        self.placed_on = placed_on
        self.deliverd_on = deliverd_on
        

@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/posts/<int:id>', methods = ['GET'])
def details(id):
    print "Logging"
    return render_template('post_details.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email, first_name, last_name, name, gender, profile_url = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, 
            nickname=username, 
            email=email, 
            first_name=first_name,
            last_name=last_name,
            profile_url=profile_url,
            name=name,
            gender=gender )
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))


# Create the Flask-Restless API manager.
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.

manager.create_api(User, methods=['GET', 'POST', 'PATCH', 'DELETE'])

manager.create_api(Post, methods=['GET', 'POST', 'PATCH', 'DELETE'], results_per_page=1000)

manager.create_api(Product, methods=['GET', 'POST', 'PATCH', 'DELETE'], results_per_page=1000)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
