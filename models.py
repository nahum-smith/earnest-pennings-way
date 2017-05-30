# Start by importing the datetime and regex module
import datetime, re

# import the database object that we created in the app module
# this db object is part of the SQLAlchemy class which is part of the
# Flask-SQLAlchemy extenion
from app import db, login_manager, bcrypt

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))
# Slugify gives blog entries a nice readable URL
def slugify(s):
    return re.sub('[^\w]+', '-', s).lower()

entry_tags = db.Table('entry_tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('entry_id', db.Integer, db.ForeignKey('entry.id'))
)
# normal class that extends the db.Model
# inherits a variety of helpers
class Entry(db.Model):
    STATUS_PUBLIC = 0
    STATUS_DRAFT = 1
    STATUS_DELETED = 2
    # primary key for database; set automatically when new blog entry
    # is created; autoincrementing
    id = db.Column(db.Integer, primary_key=True)
    # The title for the blog entry; max-length = 100 characters
    title = db.Column(db.String(100))
    # URL friendly representation of the title
    slug = db.Column(db.String(100), unique=True)
    # Content of the post stored in a text column (no max value)
    body = db.Column(db.Text)
    status = db.Column(db.SmallInteger, default=STATUS_PUBLIC)
    created_timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    modified_timestamp = db.Column(
        db.DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now
    )
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tags = db.relationship('Tag', secondary=entry_tags, backref=db.backref('entries', lazy='dynamic'))

    # Override the constructor for the class to automatically sets slug based on title
    def __init__(self, *args, **kwargs):
        super(Entry, self).__init__(*args, **kwargs) # call the parent constructor
        self.generate_slug()

    def generate_slug(self):
        self.slug = ''
        if self.title:
            self.slug = slugify(self.title)

    def __repr__(self):
        return '<ENTRY: {}>'.format(self.title)
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    slug = db.Column(db.String(64), unique=True)

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)
        self.slug = slugify(self.name)

    def __repr__(self):
        return '<Tag {}>'.format(self.name)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(255))
    name = db.Column(db.String(64))
    slug = db.Column(db.String(64), unique=True)
    active = db.Column(db.Boolean, default=True)
    created_timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    entries = db.relationship('Entry', backref='author', lazy='dynamic')
    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self):
        if self.name:
            self.slug = slugify(self.name)
    def get_id(self):
        return unicode(self.id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    @staticmethod
    def make_password(plaintext):
        return bcrypt.generate_password_hash(plaintext)

    def check_password(self, raw_password):
        return bcrypt.check_password_hash(self.password_hash, raw_password)

    @classmethod
    def create(cls, email, password, **kwargs):
        return User(
        email=email,
        password_hash=User.make_password(password),
        **kwargs)

    @staticmethod
    def authenticate(email, password):
        user = User.query.filter(User.email == email).first()
        if user and user.check_password(password):
            return user
        return False
