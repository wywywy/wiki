# _*_ coding:utf-8 _*_

from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import JSONWebSignatureSerializer, TimedJSONWebSignatureSerializer
from config import Config


class Permission(object):
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0X04
    FAVORITE_POST = 0X08
    ADMINISTRATOR = 0x80


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime,default=datetime.utcnow)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    permission = db.Column(db.Integer)
    default = db.Column(db.Boolean, default=False, index=True)
    user = db.relationship('User',
                           backref=db.backref('role'), lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'Users': (Permission.FOLLOW |
                      Permission.COMMENT |
                      Permission.WRITE_ARTICLES, True),
            'Administrator': (0x80, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
                role.permission = roles[r][0]
                role.default = roles[r][1]
                db.session.add(role)
        db.session.commit()


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), unique=True)
    content = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    favorite_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    comment = db.relationship('Comment',
                              backref=db.backref('post'), lazy='dynamic')

    def __inti__(self, title, content):
        self.title = title
        self.content = content

    def __repr__(self):
        return '<post> %r' % self.title


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    role_id = db.Column(db.Integer,  db.ForeignKey('roles.id'))
    authenticated = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post',
                            foreign_keys=[Post.author_id],
                            backref=db.backref('author'), lazy='dynamic')
    comments = db.relationship('Comment',
                               backref=db.backref('author'), lazy='dynamic')
    #关注其他作者和被其他作者关注
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('followers', lazy='joined'),
                               lazy='dynamic')
    #关注/收藏文章
    favorite = db.relationship('Post',
                               foreign_keys=[Post.favorite_id],
                               backref=db.backref('favorities'), lazy='dynamic')

    def __init__(self, username, email):
        self.username = username
        self.email = email
        if self.role is not None and self.email == Config.FlASKR_ADMIN:
            self.role = Role.query.filter_by(permission=0x80).first()


    def __repr__(self):
        return '<User %r>' % self.id

    def generate_password_hash(self, password):
        s = JSONWebSignatureSerializer(Config.SECRET_KEY)
        self.password_hash = s.dumps(password)
        return self.password_hash

    def verify_password(self, password):
        s = JSONWebSignatureSerializer(Config.SECRET_KEY)
        return s.dumps(password)  == self.password_hash

    def change_password(self, new_password):
        self.password_hash = self.generate_password_hash(new_password)
        db.session.add(self)

    def generate_email_change_token(self, expiration=3600):
        s = TimedJSONWebSignatureSerializer(Config.SECRET_KEY, expires_in=expiration)
        return s.dumps({'change_email': self.id})

    def change_email(self, token, new_email):
        s = TimedJSONWebSignatureSerializer(Config.SECRET_KEY)
        try:
            data = s.loads()
        except:
            return False
        if data['change_email'] != self.id:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def generate_email_token(self, expiration=3600):
        s = TimedJSONWebSignatureSerializer(Config.SECRET_KEY, expires_in=expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = TimedJSONWebSignatureSerializer(Config.SECRET_KEY)
        try:
            data = s.loads(token)
        except:
            return False
        if data['confirm'] != self.id:
            return False
        self.authenticated = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = TimedJSONWebSignatureSerializer(Config.SECRET_KEY, expires_in=expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = TimedJSONWebSignatureSerializer(Config.SECRET_KEY)
        try:
            data = s.loads(token)
        except:
            return False
        if data['reset'] != self.id:
            return False
        self.password_hash = self.generate_password_hash(new_password)
        db.session.add(self)
        return True


    def can(self, permissions):
        return self.role is not None and \
               (self.role.permission & permissions) == permissions

    @property
    def is_administrator(self):
        return self.can(Permission.ADMINISTRATOR)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class AnonymousUser(AnonymousUserMixin):
    pass
login_manager.anonymous_user = AnonymousUser


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    posts = db.relationship('Post',
                            backref=db.backref('category'), lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % self.name


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return '<Comment %r>' % self.content







