from web_app import db
from web_app import bcrypt
from web_app import login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(20))
    budget = db.Column(db.Integer, nullable=False, default=20000)
    status = db.Column(db.Integer, nullable=False, default=0)
    comments = db.relationship("Comment", backref='comment_user', lazy=True)
    transaction = db.relationship("Transaction", backref='user_transaction', lazy=True)

    @property
    def password(self):
        return self.password_hash
    
    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password)
    
    def change_status(self, status):
        self.status = status
    
    def check_password(self, got_password):
        return bcrypt.check_password_hash(self.password_hash, got_password)
    
    def change_profile(self, username, password):
        self.username = username
        self.password = password
        db.session.commit()
    
    def __repr__(self):
        return "<User %r>" % self.username
    

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Integer)
    author_comment = db.relationship("Comment", backref="com_item", lazy=True)
    transaction = db.relationship("Transaction", backref="transaction_item", lazy=True)
    
    def buy(self, current_user):
        self.amount -= 1
        current_user.budget -= self.price
        db.session.commit()

    def sell(self, user):
        self.amount += 1
        user.budget += self.price
        db.session.commit()

    def __repr__(self):
        return "<Item %r>" % self.description
    
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    author = db.Column(db.String, db.ForeignKey('user.username'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    
    @property
    def author_comment(self):
        return self.author
    
    @author_comment.setter
    def author_comment(self, username):
        self.author = username
    
    def __init__(self, comment):
        self.comment = comment
        
    def add_comment(self, user, item_id):
        self.author = user.username
        self.item_id = item_id
        db.session.add(self)
        db.session.commit()
        
    def __repr__(self):
        return f'<Comment {self.comment}>'
    

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cost = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def add_transaction(self):
        db.session.add(self)
        db.session.commit()
    
    def __repr__(self): 
        return f"<Transaction: user_id={self.user_id}>, item_id={self.item_id}, status={self.status}"
    