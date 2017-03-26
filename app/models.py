#_*_ coding:utf-8 _*_

from app import db
from datetime import datetime


class Permission(object):
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0X04
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


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(128))
    email = db.Column(db.String(128))
    role_id = db.Column(db.Integer,  db.ForeignKey('roles.id'))
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

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.id


class AnonymousUser(object):
    pass


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







