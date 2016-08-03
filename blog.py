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

# user key--need to see where this implements
def users_key(group = "default"):
    return db.Key.from_path("users", group)
########

# User datastore entity
class User(db.Model):
    username = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('username =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    username = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u

# generate random string for password
def make_salt(length = 5):
    return "".join(random.choice(string.lowercase) for i in range(length))

def make_pw_hash(username, password, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(username + password + salt).hexdigest()
    return "%s|%s" % (h, salt)

def valid_pw(name, pw, h):
    salt = h.split("|")[1]
    return h == make_pw_hash(name, pw, salt)


# functions for cookies and hashing
def hash_str(s):
    return hashlib.md5(s).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(hs):
    val = hs.split("|")[0]
    if hs == make_secure_val(val):
        return val

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):

## this is a problem line of code. Need to see where it is used
## and fix if necessary
#        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            "Set-Cookie",
            "%s = %s; Path = /" % (name,cookie_val))

    def login(self, user):
        self.set_secure_cookie("user_id", str(user.key().id()))

    def logout(self):
        self.response.headers.add_header("Set-Cookie", "user_id=; Path=/")

def render_post(response, post):
    response.out.write("<b>" + post.subject + "</b><br>")
    response.out.write(post.content)

class MainPage(BlogHandler):
  def get(self):
      self.write("Hello, Udacity!")

# set blog key in case we decide to have additional blogs

def blog_key(name = "default"):
    return db.Key.from_path("blogs", name)

# datastore for posts

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    # added this field to track which posts belong to user
    poster = db.StringProperty(required = True)

# show the post page and content, replacing hard returns with html <br>
    def render(self):
        self._render_text = self.content.replace("\n", "<br>")
        return render_str("post.html", p = self)

# front page of blog at /blog, display 10 latest posts

class BlogFront(BlogHandler):
    def get(self):
        # posts = Post.all().order('-created')
        # self.render('front.html', posts = posts)
        posts = db.GqlQuery("select * from Post order by created desc limit 10")
        self.render("front.html", posts = posts)

# get the selected post from the current blog

class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path("Post", int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post = post)


# pertaining to creating a new post
class NewPost(BlogHandler):
    # if the user is logged in, go to the newpost page, otherwise,
    # redirect to login

    # trying to create a newpost button and pass the username
    # so we can attach the user to the post
    def get(self):
#        if self.user:
        poster = self.request.get("poster")
        self.render("newpost.html", poster = poster)
#        else:
#            self.redirect("/login")

    # upon submission of new post: if the user is logged out
    # go to the front page of blog, otherwise, check to see
    # if content is valid, if so redirect to the new post permalink
    # page
    def post(self):
        # if not self.user:
        #     self.redirect("/blog")

        subject = self.request.get("subject")
        content = self.request.get("content")
        poster = self.request.get("poster")

        if subject and content:
            # TODO: improve by seeing if I can get the key
            # directly from cookie or previous pages
            p = Post(parent = blog_key(), subject = subject, content = content, poster = poster)
            p.put()
            self.redirect("/blog/%s" % str(p.key().id()))
        else:
            error = "Please enter both a subject and content."
            self.render("newpost.html", subject = subject, content = content, error = error)

# functions to validate username, password, and email
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

# check to see if the user is already in the database
# query the users table, count the results and if there is a result return error
def new_user(username):
    user = User.all().filter("username = ", username)
    result = user.count()
    return result

# this function checks for a matching username/password pair. Should return 0
# if no match or 1 if there is a match. Then check the hash of the username and
# password against the hash plus salt in the db
def get_pw_val(username,password):
    result = 0
    user = User.all().filter("username = ", username)
    result = user.count()
    if result == 1:
        for p in user.run(limit=1):
            h = p.pw_hash
        return valid_pw(username, password, h)
    else:
        return False

# pertaining to sign up functionality
class Signup(BlogHandler):
    # show the signup form
    def get(self):
        self.render("signup.html")

    # after user enters sign up info, verify valid input
    def post(self):
        have_error = False
        self.username = self.request.get("username")
        self.password = self.request.get("password")
        self.verify = self.request.get("verify")
        self.email = self.request.get("email")

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params["error_username"] = "That's not a valid username."
            have_error = True
        elif new_user(self.username) >= 1:
            params["error_username"] = "That user already exists."
            have_error = True

        if not valid_password(self.password):
            params["error_password"] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params["error_verify"] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params["error_email"] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render("signup.html", **params)
        else:
            pw_hash = make_pw_hash(self.username,self.password)
                # save the signup info for the blog (is this so we can have multiple blogs?)
            u = User(pw_hash = pw_hash, username = self.username, email = self.email)
            #     # save the new object to datastore
            u.put()

            self.login(u)
            self.render("signup_welcome.html", username = self.username)

class Login(BlogHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        have_error = False
        username = self.request.get("username")
        password = self.request.get("password")

        params = dict(username = username,
                      password = password)

        if new_user(username) != 1:
            params['error_username'] = "That user doesn't have an account."
            have_error = True

        if have_error:
            self.render("login.html", **params)
        else:
            pass_check_result = get_pw_val(username,password)
            if pass_check_result == True:
                user = User.all().filter("username = ", username).get()
   # then need to check posting functionality
   # then dress it up
                my_key = str(user.key().id())
                self.set_secure_cookie("user_id", my_key)
                self.render("login_welcome.html", username = username, poster = my_key)
            else:
                params['error_password'] = "Please check your password."
                have_error = True
                self.render("login.html", **params)

class Logout(BlogHandler):
    def get(self):
            self.response.headers.add_header("Set-Cookie", "user_id=; Path=/")
            self.redirect("/blog")


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/blog/signup', Signup),
                               ('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/newpost', NewPost),
                               ('/blog/login', Login),
                               ('/blog/logout', Logout)
                               ],
                              debug=True)
