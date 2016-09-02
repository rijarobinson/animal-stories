#Animal Stories Multi-User Blog
###(In fullfillment of Udacity's Full Stack Developer Program)

I developed this multi-user blog as part of Udacity's Full Stack Developer Nanodegree. I chose to create an "Animal Stories" themed blog because animals have been central to my life, and people LOVE sharing their animal stories.

#Features Overview
------------------------
Visitors may browse the sites without signing up. This allows them to look at the list of posts, view each post individually and view comments and likes (wags). A visitor must sign up for an account for additional features of the site.

##Sign Up
------------------------
Visitors can sign up for an account, creating a user name, password and email address. The sign up functionality includes validation of data entered for proper user name, password, and email syntax. User name and password are required. System checks to make sure passwords match and will return errors where invalid information is provided. If a visitor tries to create an account using a previously-created user name, an error will be returned informing the visitor as such.

##Log In
------------------------
Users who have signed up previously may access their account information without re-signing up by logging in. The site retrieves their information using their log in credentials provided and verifies that the user name and password match to an existing user. If the user is not located, an error is returned and the user may choose to re-enter their information or create an account using the "Sign Up" button. If the password and user do not match, and error pertaining to the password will be displayed.

##Security
------------------------
Passwords are stored securely, user names are unique, and user cookie is set securely.

##Blog Posts
------------------------
Signed-in users can create an animal story with a subject and content. If a user is not signed in and tries to access the page directly, they are redirected to the main blog page with a "Sign Up" button.

Signed-in users can delete and edit their own posts, either from the main page or detail page. Deleting the post deletes all associated comments (see "Comments" section). Editing function is checks for blank information and returns an error and opportunity for re-edit if the post subject or content is erased.

Visitors (non-signed in guests) and post non-originators do not see the buttons for deleting and editing a particular post.

##Comments
------------------------
Signed-in users can comment on any post, including their own. They can add comments by clicking the "Comment" button either while viewing the main list of posts or on the detail page of the post. They will be taken to the post detail page with a box for inputting the comment. They can save or cancel the comment.

Comments can be edited and deleted by their originators. Non-originators or guests will not see these options.

##Wags
------------------------
A signed-in user can "Wag" at posts (like a post) for anyone other than their own. A color picture of a dog's tail indicates an "Unwagged" post by the current signed-in user. A checkmark appears on the picture when a post has been wagged by the current-signed in user to indicate that they have already given the post a wag. If the user clicks on the checkmarked dog tail, the post will be "Unwagged". Visitors and users viewing their own posts, will see a red overlay on the dog tail picture.

##Logging Out
------------------------
When a user selects the Log Out button, the cookies indicating an active user and the user's name are deleted and all signed in functions are disabled. The visitor can still browse posts, but can't create new posts, comment on posts, or wag at posts.

##Technologies
------------------------
This site uses Google App Engine (GAE), Python, JavaScript, and bootstrap framework. Libraries used are described below Folders and Files section.

##Folders & Files
------------------------
* app.yaml
* blog.py
* index.yaml
* templates/base.html
* templates/editcomment.html
* templates/front.html
* templates/login.html
* templates/newpost.html
* templates/permalink.html
* templates/post.html
* templates/signup.html
* templates/welcome.html
* css/bootstrap.css
* css/style.css
* css/bootstrap.min.css
* images (folder)

**blog.py** is the main python file that contains the code for running the app.

**app.yaml and index.yaml** are used by GAE. Please refer to GAE documention regarding these files.

**templates/base.html** contains the base template for the site.

**templates/front.html** displays the main site page. The post.html is displayed within this page.

**templates/permalink.html** displays the individual post. Post.html is also used within this page. This page contains commenting functionality. It is also displayed after a new post is created.

**templates/post.html** is contained within the front and permalink html files and displays the details of an individual post.

**templates/newpost.html** is the form that allows for creating a new animal story. It is also used when a user edits their own post.

**templates/editcomment.html** is a form that is used when a user edits their own comment.

**templates/login.html** is for an existing user to login.

**templates/signup.html** is for a new user to create an account.

**templates/welcome.html** displays a welcome message to the new or existing user.

**css/bootstrap.css** contains the framework style code. This file is not directly referenced by the website. It is the full version of bootstrip.min.css for development use and has not been modified. Final version of website will not include this file.

**css/bootstrap.min.css** contains the minified version of bootstrap.css and is not modified from it's original version. Any style changes are in the style.css file.

**css/style.css** contains the modifications and additions to the style code.

**images** folder contains the images required for the site.

##Libraries & Modules
* os
* re
* webapp2
* jinja2
* random
* string
* hashlib
* time
* db (from GAE)

##Using the Site
**To run the site**, place all files in the same folder with the same structure provided. Create a new application on the GAE Cloud Platform. Rename the application from animal stories to your GAE application name in the **app.yaml** file. Use desktop GAE to Add the application and run locally or deploy. Please see GAE documentation for further information.

**To customize the files**, you can open the **base.html** file in your favorite text editor and make changes as desired. You can review the references to bootstrap using the bootstrap.css file, but good practice is to make modifications/additions in a separate css file (in this case, you can change the style.css file). Save the files and refresh the site to see your new web page.

Mockup/basic design ideas for this application were provided by [Udacity](http://www.Udacity.com). Additional instruction on Front End Development is available by signing up for a class on their site. Bootstrap provides the framework,and Google App Engine serves the content. Additional enhancements by Marija Robinson.

The implemented project can be accessed at [http://animal-stories.appspot.com/blog](animal-stories.appspot.com).

I welcome any feedback on this project at marija@springmail.com.