
from google.appengine.ext import db

# User datastore entity
class User(db.Model):
    username = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

class Wags(db.Model):
    wagged_user = db.StringProperty()
    wagged_post = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

class Comments(db.Model):
    comment_user = db.StringProperty()
    comment_post = db.StringProperty()
    comment_text=db.TextProperty()
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

# datastore for posts
class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    # added this field to track which posts belong to user
    poster = db.StringProperty(required = True)
    wags = db.IntegerProperty(default=0)

# show the post page and content, replacing hard returns with html <br>
    def render(self):
        self._render_text = self.content.replace("\n", "<br>")
        return render_str("post.html", p = self)
