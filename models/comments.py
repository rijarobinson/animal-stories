from google.appengine.ext import db


class Comments(db.Model):
    comment_user = db.StringProperty()
    comment_post = db.StringProperty()
    comment_text=db.TextProperty()
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
