import os
import re
from string import letters
import webapp2
import jinja2

# random, string, hashlib used for salted hashed password generation
import random
import string
import hashlib


from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


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

    def render(self):
        self._render_text = self.content.replace("\n", "<br>")
        return render_str("post.html", p = self)