from google.appengine.ext import db


class Wags(db.Model):
    wagged_user = db.StringProperty()
    wagged_post = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)