from google.appengine.ext import db


class User(db.Model):
    username = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()