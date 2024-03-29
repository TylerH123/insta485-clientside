"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485
from insta485 import model


@insta485.app.route('/uploads/<path:name>')
def retrieve_image(name):
    """Send image link."""
    if 'login' in flask.session:
        filename = insta485.app.config['UPLOAD_FOLDER']/name
        if not model.is_file(filename):
            flask.abort(404)
        return flask.send_from_directory(
            insta485.app.config['UPLOAD_FOLDER'], name, as_attachment=True
        )
    return flask.abort(403)


@insta485.app.route('/')
def show_index():
    """Display / route."""
    if 'login' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    login_user = flask.session['login']
    context = {
        'logname': login_user,
        'posts': []
    }
    posts = model.get_posts(login_user)

    # Get all relevant data for each post
    for post in posts:
        postid = post['postid']
        post_data = model.get_post_data(postid)
        post_data['not_liked'] = model.user_like_post(login_user, postid) == 0
        context['posts'].append(post_data)
    return flask.render_template('index.html', **context)


@insta485.app.route('/users/<path:username>/')
def show_user(username):
    """Display /users/<username> route."""
    if 'login' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    login_user = flask.session['login']
    context = {
        'logname': login_user,
        'username': username,
    }
    user_data = model.get_user_data(username)
    if user_data is None:
        flask.abort(404)
    context['fullname'] = user_data['fullname']
    followers = model.get_user_followers(username)
    context['logname_follows_username'] = context['logname'] in followers
    posts = model.get_user_posts(username)
    context['posts'] = posts
    context['total_posts'] = len(posts)
    context['followers'] = len(followers)
    context['following'] = len(model.get_user_following(username))

    return flask.render_template('user.html', **context)


@insta485.app.route('/posts/<path:postid>/')
def show_posts(postid):
    """Display /posts/<postid>/ route."""
    if 'login' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    login_user = flask.session['login']
    post = model.get_post_data(postid)
    context = {
        'logname': login_user,
        'postid': postid
    }

    for entry in post:
        context[entry] = post[entry]
    post_owner = post['owner']
    context['is_owner'] = post_owner == login_user
    context['not_liked'] = model.user_like_post(login_user, postid) == 0
    return flask.render_template('post.html', **context)


@insta485.app.route('/users/<path:username>/followers/')
def show_followers(username):
    """Display /users/<username>/follower route."""
    if 'login' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    login_user = flask.session['login']
    context = {
        'logname': login_user,
        'followers': []
    }

    logname_following_list = model.get_user_following(context['logname'])
    followers_list = model.get_user_followers(username)

    # Get all users following username
    for follower in followers_list:
        user = {
            'username': follower,
            'logname_follows_username': follower in logname_following_list
        }
        user['user_img_url'] = '/uploads/' + model.get_user_photo(follower)
        context['followers'].append(user)

    return flask.render_template('followers.html', **context)


@insta485.app.route('/users/<path:username>/following/')
def show_following(username):
    """Display /users/<userid>/following route."""
    if 'login' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    login_user = flask.session['login']
    context = {
        'logname': login_user,
        'following': []
    }
    logname_following_list = model.get_user_following(context['logname'])
    following_list = model.get_user_following(username)
    # Get all users that username follows
    for following in following_list:
        user = {
            'username': following,
            'user_img_url': '',
            'logname_follows_username': following in logname_following_list
        }
        user['user_img_url'] = '/uploads/' + model.get_user_photo(following)
        context['following'].append(user)

    return flask.render_template('following.html', **context)


@insta485.app.route('/explore/')
def show_explore():
    """Display /explore/ route."""
    if 'login' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    login_user = flask.session['login']
    context = {
        'logname': login_user,
        'not_following': []
    }
    not_following_list = model.get_user_not_following(context['logname'])
    # Get all users that username follows
    for notfollowing in not_following_list:
        user = {
            'username': notfollowing,
            'user_img_url': '',
        }
        user['user_img_url'] = '/uploads/' + model.get_user_photo(notfollowing)
        context['not_following'].append(user)

    return flask.render_template('explore.html', **context)


@insta485.app.route('/accounts/login/')
def show_login():
    """Display login route."""
    if 'login' in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    context = {
        'login': True
    }
    return flask.render_template('login.html', **context)


@insta485.app.route('/accounts/logout/', methods=["POST"])
def logout():
    """Display logout route."""
    if 'login' in flask.session:
        flask.session.pop('login')
    return flask.redirect(flask.url_for("show_login"))


@insta485.app.route('/accounts/create/')
def show_create():
    """Display create account route."""
    if 'login' in flask.session:
        return flask.redirect(flask.url_for('show_edit'))
    context = {
        'login': True
    }
    return flask.render_template('create.html', **context)


@insta485.app.route('/accounts/edit/')
def show_edit():
    """Display edit account route."""
    if 'login' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    login_user = flask.session['login']
    context = {
        'logname': login_user,
        'user_filename': '/uploads/' + model.get_user_photo(login_user),
        **model.get_user_data(login_user),
    }
    return flask.render_template('edit.html', **context)


@insta485.app.route('/accounts/password/')
def show_password():
    """Display password change route."""
    if 'login' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    login_user = flask.session['login']
    context = {
        'logname': login_user
    }
    return flask.render_template('password.html', **context)


@insta485.app.route('/accounts/delete/')
def show_delete():
    """Display delete account route."""
    if 'login' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    login_user = flask.session['login']
    context = {
        'logname': login_user
    }
    return flask.render_template('delete.html', **context)


@insta485.app.route('/accounts/', methods=['POST'])
def update_accounts():
    """Display login route."""
    operation = flask.request.form['operation']
    redirect = flask.url_for('show_index')
    if 'target' in flask.request.args:
        redirect = flask.request.args['target']
    if operation == 'login':
        return login(redirect)
    if operation == 'create':
        return create(redirect)
    if operation == 'edit_account':
        return edit(redirect)
    if operation == 'update_password':
        return update(redirect)
    if operation == 'delete':
        return delete(redirect)
    return flask.abort(404)


@insta485.app.route('/likes/', methods=['POST'])
def update_likes():
    """Display likes route."""
    if 'login' not in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    operation = flask.request.form['operation']
    redirect = flask.url_for('show_index')
    if 'target' in flask.request.args:
        redirect = flask.request.args['target']
    if operation == 'like':
        login_user = flask.session['login']
        postid = flask.request.form.get('postid')
        if postid is None:
            flask.abort(404)
        if not model.user_like_post(login_user, postid):
            model.create_like(login_user, postid)
        else:
            flask.abort(409)
        return flask.redirect(redirect)
    if operation == 'unlike':
        login_user = flask.session['login']
        postid = flask.request.form['postid']
        if model.user_like_post(login_user, postid):
            model.delete_like(login_user, postid=postid)
        else:
            flask.abort(409)
        return flask.redirect(redirect)
    return flask.abort(404)


@insta485.app.route('/comments/', methods=['POST'])
def update_comments():
    """Display comments route."""
    if 'login' not in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    operation = flask.request.form['operation']
    redirect = flask.url_for('show_index')
    if 'target' in flask.request.args:
        redirect = flask.request.args['target']
    if operation == 'create':
        login_user = flask.session['login']
        postid = flask.request.form.get('postid')
        text = flask.request.form.get('text')
        if postid is None or text is None or postid == '' or text == '':
            flask.abort(400)
        model.create_comment(login_user, postid, text)
        return flask.redirect(redirect)
    if operation == 'delete':
        login_user = flask.session['login']
        if 'commentid' not in flask.request.form:
            flask.abort(400)
        commentid = flask.request.form['commentid']
        comment_owner = model.get_comment_owner(commentid)['owner']
        if login_user == comment_owner:
            model.delete_comment(login_user, commentid)
        else:
            flask.abort(403)
        return flask.redirect(redirect)
    return flask.abort(404)


@insta485.app.route('/posts/', methods=['POST'])
def update_posts():
    """Display posts route."""
    if 'login' not in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    operation = flask.request.form['operation']
    login_user = flask.session['login']
    redirect = f'/users/{login_user}/'
    if 'target' in flask.request.args:
        redirect = flask.request.args['target']
    if operation == 'create':
        fileobj = flask.request.files.get('file')
        if fileobj is None or fileobj.filename == '':
            flask.abort(400)
        filename = model.upload_file(fileobj)
        model.create_post(login_user, filename)
        return flask.redirect(redirect)
    if operation == 'delete':
        postid = flask.request.form.get('postid')
        if postid is None:
            flask.abort(400)
        data = model.get_post_data(postid)
        filename = model.get_post_filename(postid)
        post_owner = data['owner']
        if login_user == post_owner:
            model.delete_post(postid, filename)
        else:
            flask.abort(403)
        return flask.redirect(redirect)
    return flask.abort(404)


@insta485.app.route('/following/', methods=['POST'])
def update_follows():
    """Display follows route."""
    if 'login' not in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    operation = flask.request.form['operation']
    redirect = flask.url_for('show_index')
    if 'target' in flask.request.args:
        redirect = flask.request.args['target']
    login_user = flask.session['login']
    if operation == 'follow':
        return follow(redirect, login_user)
    if operation == 'unfollow':
        return unfollow(redirect, login_user)
    return flask.abort(404)


def login(redirect):
    """Login."""
    password = flask.request.form.get('password')
    username = flask.request.form.get('username')
    if username is None or password is None or \
       username == '' or password == '':
        flask.abort(400)
    data = model.get_user_data(username)
    if data is None:
        flask.abort(403)
    hashed_pass = model.hash_password(password,
                                      data['password'].split('$')[1])
    if data['password'] != hashed_pass:
        flask.abort(403)
    flask.session['login'] = username
    return flask.redirect(redirect)


def create(redirect):
    """Create account."""
    data = []
    fields = ['username', 'fullname', 'email', 'password', 'file']
    for field in fields:
        if field == 'file':
            fileobj = flask.request.files.get(field)
            if fileobj is None or fileobj.filename == '':
                flask.abort(400)
            data_field = model.upload_file(fileobj)
        else:
            data_field = flask.request.form.get(field)
            if data_field is None or data_field == '':
                flask.abort(400)
            if field == 'password':
                data_field = model.hash_password(data_field)
        data.append(data_field)
    existing_username = model.get_user_data(data[0])
    if existing_username is not None:
        flask.abort(409)
    model.create_new_user(data)
    flask.session['login'] = data[0]
    return flask.redirect(redirect)


def edit(redirect):
    """Edit account."""
    if 'login' not in flask.session:
        flask.abort(403)
    data = []
    fields = ['fullname', 'email', 'file']
    data.append(flask.session['login'])
    for field in fields:
        if field == 'file':
            fileobj = flask.request.files.get(field)
            if fileobj is None or fileobj.filename == "":
                data_field = ""
            else:
                data_field = model.upload_file(fileobj)
        else:
            data_field = flask.request.form.get(field)
            if data_field is None or data_field == '':
                flask.abort(400)
        data.append(data_field)
    model.edit_user_profile(data)
    return flask.redirect(redirect)


def update(redirect):
    """Update password."""
    if 'login' not in flask.session:
        flask.abort(403)
    old_pass = flask.request.form.get('password')
    new_pass1 = flask.request.form.get('new_password1')
    new_pass2 = flask.request.form.get('new_password2')

    def check_pass():
        if old_pass is None or new_pass1 is None or \
           new_pass2 is None:
            flask.abort(400)
        if old_pass == '' or new_pass1 == '' or \
           new_pass2 == '':
            flask.abort(400)
    check_pass()
    login_user = flask.session['login']
    data = model.get_user_data(login_user)
    hashed_pass = model.hash_password(old_pass,
                                      data['password'].split('$')[1])
    if data['password'] != hashed_pass:
        flask.abort(403)
    if new_pass1 != new_pass2:
        flask.abort(401)
    hashed_new_pass = model.hash_password(new_pass1)
    model.update_password(login_user, hashed_new_pass)
    return flask.redirect(redirect)


def delete(redirect):
    """Delete account."""
    if 'login' not in flask.session:
        flask.abort(403)
    login_user = flask.session['login']
    data = model.get_user_data(login_user)
    if data is not None:
        model.delete_user(login_user)
    flask.session.pop('login')
    return flask.redirect(redirect)


def follow(redirect, logname):
    """Follow users."""
    username = flask.request.form.get('username')
    if username is None or username == '':
        flask.abort(400)
    data = model.get_user_following(logname)
    if username in data:  # logname already follows username
        flask.abort(409)
    model.set_follows(logname, username)
    return flask.redirect(redirect)


def unfollow(redirect, logname):
    """Unfollow users."""
    username = flask.request.form.get('username')
    if username is None or username == '':
        flask.abort(400)
    data = model.get_user_following(logname)
    if username not in data:  # logname does not follow username
        flask.abort(409)
    model.delete_follows(logname, username)
    return flask.redirect(redirect)
