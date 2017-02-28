from google.appengine.ext import db

from rendering import template_dir, jinja_env, render_str

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    # added this field to track which posts belong to user
    poster = db.StringProperty(required = True)
    wags = db.IntegerProperty(default=0)

    def render(self):
        self._render_text = self.content.replace("\n", "<br>")
        return render_str("post.html", p = self)