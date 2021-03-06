import os
import re
from string import letters
import webapp2
import jinja2
import json

# random, string, hashlib used for salted hashed password generation
import random
import string
import hashlib

import time

# TODO
# time library is to create short delay before reloading to compensate for
# eventual consistency. This is a temporary fix until
# I can better understand ancestor queries


from google.appengine.ext import db

from models import User, Wags, Comments, Post, render_str


def users_key(group = "default"):
    return db.Key.from_path("users", group)

class AddWag(webapp2.RequestHandler):
    def get(self):
        logged_in = self.request.cookies.get("current_user")
        if logged_in:
            self.redirect("/blog")
        else:
            self.redirect("/blog/login")

    def post(self):
        wagged_user = self.request.cookies.get("current_user")
        logged_in = self.request.cookies.get("current_user")
        if logged_in:
            data = json.loads(self.request.body)
            post_to_wag = Post.get_by_id(int(data['storyKey']), parent = blog_key())
            # post_to_wag = Post.Key(Post, data['storyKey']).get()
            p = Wags(parent = blog_key(), wagged_user = wagged_user,
                wagged_post = data['storyKey'])
            p.put()

    # updates wag field.
            current_wags = post_to_wag.wags
            new_wags = current_wags + 1
            post_to_wag.wags = new_wags
            post_to_wag.put()
            self.response.out.write(json.dumps({'posts': {'wags': new_wags, 'storyKey': int(data['storyKey'])}}))
        else:
            self.redirect("/blog/login")


class RemoveWag(webapp2.RequestHandler):
    def get(self):
        logged_in = self.request.cookies.get("current_user")
        if logged_in:
            self.redirect("/blog")
        else:
            self.redirect("/blog/login")

    def post(self):
        data = json.loads(self.request.body)
        unwagged_user = self.request.cookies.get("current_user")
        unwagged_post = data['postKey']
        # unwagged user also gets the logged in user
        if unwagged_user:
            unwag = db.GqlQuery("SELECT * from Wags WHERE wagged_post = :1 "
                + "AND wagged_user = :2", unwagged_post, unwagged_user)
            db.delete(unwag)
            post_to_unwag = Post.get_by_id(int(data['postKey']), parent = blog_key())
            current_wags = post_to_unwag.wags
            new_wags = (current_wags - 1)
            post_to_unwag.wags = new_wags
            post_to_unwag.put()
            self.response.out.write(json.dumps({'posts': {'wags': new_wags, 'postKey': int(data['postKey'])}}))
        else:
            self.redirect("/blog/login")


class DeletePost(webapp2.RequestHandler):
    def get(self):
        logged_in = self.request.cookies.get("current_user")
        if logged_in:
            self.redirect("/blog")
        else:
            self.redirect("/blog/login")

    def post(self):
        user_who_deleted = self.request.cookies.get("current_user")
        post_to_delete = self.request.get("post_key")
        micro_check = self.request.cookies.get("microchip")
        delete_record = Post.get_by_id(int(post_to_delete),
            parent = blog_key())
        post_poster = make_microchip_hash(delete_record.poster)
        # user_who_deleted gets the current logged in user
        if micro_check == post_poster:
            db.delete(delete_record)
            delete_related_comments=db.GqlQuery("SELECT * from Comments WHERE "
                + "comment_post = :1", post_to_delete)
            db.delete(delete_related_comments)
            self.redirect("/blog")
        else:
            self.redirect("/blog/login")

class DeleteComment(webapp2.RequestHandler):
    def get(self):
        logged_in = self.request.cookies.get("current_user")
        if logged_in:
            self.redirect("/blog")
        else:
            self.redirect("/blog/login")

    def post(self):
        user_who_deleted = self.request.cookies.get("current_user")
        comment_to_delete = self.request.get("comment_key")
        current_post = self.request.get("post_key")
        micro_check = self.request.cookies.get("microchip")
        delete_record = Comments.get_by_id(int(comment_to_delete),
            parent = blog_key())
        comment_poster = make_microchip_hash(delete_record.comment_user)
        # user_who_deleted gets the current logged in user
        if micro_check == comment_poster:
            db.delete(delete_record)
            self.redirect("/blog/" + current_post)
        else:
            self.redirect("/blog/login")

# generate random string for password
def make_salt(length = 5):
    return "".join(random.choice(string.lowercase) for i in range(length))

def make_microchip_hash(s):
    hm = hash_str(s)
    return hm

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
        params["user"] = self.request.get("username")
        params["current_user"] = self.request.cookies.get("current_user")
        params["comment"] = self.request.get("comment")
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

def render_post(response, post):
    response.out.write("<b>" + post.subject + "</b><br>")
    response.out.write(post.content)
    response.out.write(post.poster)

class MainPage(BlogHandler):
  def get(self):
      self.redirect("/blog")

# set blog key in case we decide to have additional blogs
def blog_key(name = "default"):
    return db.Key.from_path("blogs", name)

# front page of blog at /blog, display 10 latest posts
class BlogFront(BlogHandler):
    def get(self):
        posts = Post.all().order('-created')
        front_page=1
        logged_in = self.request.cookies.get("current_user")
        current_user = self.request.cookies.get("current_user")
        user_wags = db.GqlQuery("SELECT wagged_post from Wags WHERE "
            + "wagged_user = :1", current_user)
        myList = []
        for u in user_wags:
            myList.append(u.wagged_post)
            time.sleep(0.2)
        self.render("front.html", posts = posts, logged_in = logged_in,
            current_user = current_user, myList = myList,
            front_page = front_page)

class EditPost(BlogHandler):
    def get(self):
        poster = self.request.get("poster")
        post_to_edit = self.request.get("post_key")
        subject = self.request.get("subject")
        content = self.request.get("content")
        logged_in = self.request.cookies.get("current_user")
        if logged_in == poster:
            if post_to_edit:
                self.render("editpost.html", subject = subject, content = content,
                    poster = poster, post_to_edit = post_to_edit, newpost_page = 1,
                    logged_in = logged_in)
            else:
                self.redirect("/blog")
        else:
            self.redirect("/blog/login")

    def post(self):
        poster = self.request.get("poster")
        post_to_edit = self.request.get("post_key")
        subject = self.request.get("subject")
        content = self.request.get("content")
        logged_in = self.request.cookies.get("current_user")
        if logged_in == poster:
            self.render("editpost.html", subject = subject, content = content,
                poster = poster, post_to_edit = post_to_edit, newpost_page = 1,
                logged_in = logged_in)
        else:
            self.redirect("/login")

class AddComment(BlogHandler):
    def get(self):
        logged_in = self.request.cookies.get("current_user")
        if logged_in:
            self.redirect("/blog")
        else:
            self.redirect("/blog/login")

    def post(self):
        comment_user = self.request.cookies.get("current_user")
        comment_post = self.request.get("post_key")
        comment_text = self.request.get("comment")
        # comment_user also contains logged in user info
        if comment_user:
            if comment_text:
                c = Comments(parent = blog_key(), comment_user = comment_user,
                    comment_post = comment_post, comment_text=comment_text)
                c.put()
                self.redirect("/blog/" + comment_post)
            else:
                #TODO: add error if no text added
                self.redirect("/blog/" + comment_post + "?comment=True")
        else:
            self.redirect("/blog/login")


class EditComment(BlogHandler):
    def get(self):
        logged_in = self.request.cookies.get("current_user")
        if logged_in:
            self.redirect("/blog")
        else:
            self.redirect("/blog/login")

    def post(self):
        current_user = self.request.cookies.get("current_user")
        current_post = self.request.get("post_key")
        comment_to_edit = self.request.get("comment_key")
        comment_text = self.request.get("comment_text")
        micro_check = self.request.cookies.get("microchip")
        edit_record = Comments.get_by_id(int(comment_to_edit),
            parent = blog_key())
        post_owner = make_microchip_hash(edit_record.comment_user)
        # current_user contains login info
        if micro_check == post_owner:
            self.render("editcomment.html", current_user = current_user,
                current_post = current_post, comment_to_edit = comment_to_edit,
                comment_text = comment_text)
        else:
            self.redirect("/blog/login")

class SaveComment(BlogHandler):
    def get(self):
        logged_in = self.request.cookies.get("current_user")
        if logged_in:
            self.redirect("/blog")
        else:
            self.redirect("/blog/login")

    def post(self):
        current_user = self.request.cookies.get("current_user")
        current_post = self.request.get("post_key")
        comment_to_edit=self.request.get("comment_key")
        comment_text = self.request.get("comment")
        micro_check = self.request.cookies.get("microchip")
        edit_record = Comments.get_by_id(int(comment_to_edit),
            parent = blog_key())
        comment_owner = make_microchip_hash(edit_record.comment_user)
        # current_user contains login info
        if micro_check == comment_owner:
            if comment_to_edit:
                if comment_text:
                    edit_record.comment_text = comment_text
                    edit_record.put()
                    self.redirect("/blog/" + current_post)
                else:
                    error = "Please enter the comment."
                    self.render("editcomment.html", current_user = current_user,
                        current_post = current_post,
                        comment_to_edit = comment_to_edit,
                        error = error, comment_text = comment_text)
            else:
                self.redirect("blog/" + post_key)
        else:
            self.redirect("blog/login")


class WelcomeRedirect(webapp2.RequestHandler):
    def get(self):
        self.redirect("/blog/signup")

# get the selected post from the current blog
class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path("Post", int(post_id), parent = blog_key())
        post = db.get(key)
        logged_in = self.request.cookies.get("current_user")
        comments_to_show = db.GqlQuery("SELECT * from Comments WHERE "
            + "comment_post = :1 ORDER BY created ASC", post_id)
        comment_list_count = comments_to_show.count()
        if comment_list_count >= 1:
            comment_list = comments_to_show
        else:
            comment_list = "No Comments"
        if not post:
            self.error(404)
            return
        time.sleep(0.2)
        self.render("permalink.html", post = post, comment_list = comment_list,
            permalink_page = 1, logged_in = logged_in)


# pertaining to creating a new post
class NewPost(BlogHandler):
    def get(self):
        poster = self.request.get("poster")
        logged_in = self.request.get("logged_in")
        if logged_in:
            self.render("newpost.html", poster = poster, newpost_page = 1,
                logged_in = logged_in)
        else:
            self.redirect("/blog/login")


    def post(self):
        poster = self.request.get("poster")
        subject = self.request.get("subject")
        content = self.request.get("content")
        # post_to_edit variable is in case it is an edit, will be blank if new post
        # otherwise, the inputs will fill with the values of the post
        post_to_edit = self.request.get("post_key")
        logged_in = self.request.cookies.get("current_user")
        micro_check = self.request.cookies.get("microchip")
        if post_to_edit:
            edit_record = Post.get_by_id(int(post_to_edit),
                parent = blog_key())
            post_poster = make_microchip_hash(edit_record.poster)
            if micro_check == post_poster:
                if subject and content:
                    edit_record.subject = subject
                    edit_record.content = content
                    edit_record.put()
                    self.redirect("/blog/" + post_to_edit)
                else:
                    error = "Please enter both a subject and content."
                    self.render("editpost.html", subject = subject,
                        content = content, poster = poster, error = error,
                        post_to_edit = post_to_edit, logged_in = logged_in)
            else:
                self.redirect("/blog/login")
        else:
            if subject and content:
                p = Post(parent = blog_key(), subject = subject,
                    content = content, poster = poster)
                p.put()
                self.redirect("/blog/%s" % str(p.key().id()))
            else:
                error = "Please enter both a subject and content."
                self.render("newpost.html", subject = subject,
                    content = content, poster = poster,
                    error = error, logged_in = logged_in)


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

# checks for a matching username/password pair. Should return 0
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
    def get(self):
        self.render("signup.html", sign_page = 1)

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
            u = User(pw_hash = pw_hash, username = self.username,
                email = self.email)
            u.put()
            self.login(u)
            self.response.headers.add_header("Set-Cookie",
                "%s = %s; Path = /" % ("current_user", str(self.username)))
            self.response.headers.add_header("Set-Cookie",
                "%s = %s; Path = /" % ("microchip", str(make_microchip_hash(self.username))))
            logged_in = self.username
            referred = 1
            self.render("welcome.html", username = self.username,
                referred = referred, logged_in = logged_in)

class Login(BlogHandler):
    def get(self):
        self.render("login.html", log_page = 1)
    def post(self):
        have_error = False
        username = self.request.get("username")
        password = self.request.get("password")

        params = dict(username = username,
                      password = password)

        if new_user(username) != 1:
            params["error_username"] = "That user doesn't have an account."
            have_error = True

        if have_error:
            self.render("login.html", **params)
        else:
            pass_check_result = get_pw_val(username,password)
            if pass_check_result == True:
                user = User.all().filter("username = ", username).get()
                my_key = str(user.key().id())
                self.set_secure_cookie("user_id", my_key)
                this_user = str(username)
                self.response.headers.add_header(
                    "Set-Cookie",
                    "%s = %s; Path= /" % ("current_user", this_user))
                self.response.headers.add_header(
                    "Set-Cookie",
                    "%s = %s; Path= /" % ("microchip", make_microchip_hash(this_user)))
                logged_in = this_user
                referred = 2
                self.render("welcome.html", username = username,
                    referred = referred, welcome_page = 1, logged_in = logged_in)
            else:
                params['error_password'] = "Please check your password."
                have_error = True
                self.render("login.html", **params)

class Logout(BlogHandler):
    def get(self):
            self.response.headers.add_header("Set-Cookie",
                "user_id=; Path=/")
            self.response.headers.add_header("Set-Cookie",
                "current_user=; Path=/")
            self.response.headers.add_header("Set-Cookie",
                "microchip=; Path=/")
            self.redirect("/blog/login")


app = webapp2.WSGIApplication([("/", MainPage),
                               ("/blog/signup", Signup),
                               ("/blog/?", BlogFront),
                               ("/blog/([0-9]+)", PostPage),
                               ("/blog/newpost", NewPost),
                               ("/blog/login", Login),
                               ("/blog/logout", Logout),
                               ("/blog/addwag", AddWag),
                               ("/blog/removewag", RemoveWag),
                               ("/blog/deletepost", DeletePost),
                               ("/blog/editpost", EditPost),
                               ("/blog/addcomment", AddComment),
                               ("/blog/deletecomment", DeleteComment),
                               ("/blog/editcomment", EditComment),
                               ("/blog/savecomment", SaveComment),
                               ("/blog/welcome", WelcomeRedirect)
                               ],
                              debug=True)
