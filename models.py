from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

db = SQLAlchemy()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)




class User(db.Model):
    __tablename__ = 'users'

    """class method to get specific user"""
    @classmethod
    def get_by_username(cls, username):
       return cls.query.filter_by(username=username).all()
    
    """Register"""
    @classmethod
    def register(cls, username, password):
        hashed = bcrypt.generate_password_hash(password)
        #turn bytesting into normal unicode utf8 string
        hashed_utf8= hashed.decode("utf8")
        return cls(username=username, password=hashed_utf8)

    """Log in """
    @classmethod 
    def authenticate (cls, username, password): 
        """return user if valid; else return False"""
        u = User.query.filter_by(username=username).first()
        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False


    id = db.Column(db.Integer, autoincrement=True, primary_key = True)
    username = db.Column(db.String(20), nullable=False, unique = True)
    password = db.Column(db.String, nullable=False)

    #savedrecipes=db.relationship('FavoriteRecipe', backref='user')

    #through relationship reference database, then secondary table name, and the backref so this connets all three

    recipes=db.relationship("FoundRecipe", secondary="favoriterecipes", backref="users")
    

    def greet(self):
        return f'Hi, {self.username}! Welcome Back!'

class FavoriteRecipe(db.Model):
    """Mapping user fav recipes"""
    __tablename__ = 'favoriterecipes'


    user_id  = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'),  primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('foundrecipes.id', ondelete='cascade'), primary_key=True)
    
    

class FoundRecipe(db.Model):
    """Mapping user fav recipes"""
    __tablename__ = 'foundrecipes'
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    title= db.Column(db.String, nullable = False, unique = True)
    link=db.Column(db.String, nullable=False)
    image=db.Column(db.String, nullable=False)
    cooktime=db.Column(db.String, nullable=False)
    

    savedrecipes=db.relationship('FavoriteRecipe', backref='foundrecipes')








