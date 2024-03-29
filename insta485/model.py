"""Insta485 model (database) API."""
import sqlite3
import os
import uuid
import pathlib
import hashlib
import flask
import arrow
import insta485


def dict_factory(cursor, row):
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_db():
    """Open a new database connection."""
    if 'sqlite_db' not in flask.g:
        db_filename = insta485.app.config['DATABASE_FILENAME']
        flask.g.sqlite_db = sqlite3.connect(str(db_filename))
        flask.g.sqlite_db.row_factory = dict_factory
        # Foreign keys have to be enabled per-connection.  This is an sqlite3
        # backwards compatibility thing.
        flask.g.sqlite_db.execute('PRAGMA foreign_keys = ON')
    return flask.g.sqlite_db


@insta485.app.teardown_appcontext
def close_db(error):
    """Close the database at the end of a request.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    assert error or not error  # Needed to avoid superfluous style error
    sqlite_db = flask.g.pop('sqlite_db', None)
    if sqlite_db is not None:
        sqlite_db.commit()
        sqlite_db.close()


def get_last_insert_rowid():
    """Get last insert rowid."""
    connection = get_db()
    cur = connection.execute('SELECT last_insert_rowid()')
    return cur.fetchone()['last_insert_rowid()']


# ===== LOGIN =====
def create_new_user(user_data):
    """Insert new user into table."""
    connection = get_db()
    connection.execute(
        'INSERT INTO '
        'users (username, fullname, email, filename, password) '
        'VALUES (?, ?, ?, ?, ?)',
        (user_data[0], user_data[1], user_data[2], user_data[4], user_data[3])
    )
    return True


def upload_file(fileobj):
    """Upload a file."""
    filename = fileobj.filename
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix
    uuid_basename = f'{stem}{suffix}'
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path)
    return uuid_basename


def hash_password(password, salt=None):
    """Hashes password."""
    algorithm = 'sha512'
    user_salt = salt if salt is not None else uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = user_salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = '$'.join([algorithm, user_salt, password_hash])
    return password_db_string


def is_file(file):
    """Check if file exists."""
    return os.path.exists(file)


# ===== USER =====
def get_user_data(username):
    """Get user data from table."""
    connection = get_db()
    cur = connection.execute(
        'SELECT * '
        'FROM users '
        'WHERE username = ?',
        (username, )
    )
    user_data = cur.fetchone()
    return user_data


def get_user_photo(username):
    """Get user photo link from table."""
    connection = get_db()
    cur = connection.execute(
        'SELECT filename '
        'FROM users '
        'WHERE username = ?',
        (username, )
    )
    return cur.fetchone()['filename']


def get_user_posts(username):
    """Get user's post from table."""
    connection = get_db()
    cur = connection.execute(
        'SELECT postid '
        'FROM posts '
        'WHERE owner = ?',
        (username, )
    )
    posts_data = cur.fetchall()
    posts = []
    for entry in posts_data:
        posts.append(get_post_data(entry['postid']))
    return posts


def get_user_posts_filename(username):
    """Get user's post from table."""
    connection = get_db()
    cur = connection.execute(
        'SELECT filename '
        'FROM posts '
        'WHERE owner = ?',
        (username, )
    )
    return cur.fetchall()


def get_user_followers(username):
    """Get all the followers for a user."""
    connection = get_db()
    cur = connection.execute(
        'SELECT username1 '
        'FROM following '
        'WHERE username2 = ?',
        (username, )
    )
    followers_data = cur.fetchall()
    followers = []
    for item in followers_data:
        followers.append(item['username1'])
    return followers


def get_user_following(username):
    """Get all the people that the user is following."""
    connection = get_db()
    cur = connection.execute(
        'SELECT username2 '
        'FROM following '
        'WHERE username1 = ?',
        (username, )
    )
    following_data = cur.fetchall()
    following = []
    for item in following_data:
        following.append(item['username2'])
    return following


def get_user_not_following(username):
    """Get all the users that the user is not following."""
    connection = get_db()
    cur = connection.execute(
        'SELECT username '
        'FROM users '
        'EXCEPT '
        'SELECT username2 '
        'FROM following '
        'WHERE username1 = ?',
        (username, )
    )
    not_following_data = cur.fetchall()
    not_following = []
    for item in not_following_data:
        not_following.append(item['username'])
    not_following.remove(username)
    return not_following


def edit_user_profile(data):
    """Update Fullname, Email, Profile Picture."""
    username = data[0]
    fullname = data[1]
    email = data[2]
    if data[3] == "":
        photo = get_user_photo(username)
    else:
        photo = data[3]
    connection = get_db()
    connection.execute(
        'UPDATE users '
        'SET fullname = ?, email = ?, filename = ? '
        'WHERE username = ?',
        (fullname, email, photo, username)
    )
    return True


def update_password(username, password):
    """Update password for user."""
    connection = get_db()
    connection.execute(
        'UPDATE users '
        'SET password = ? '
        'WHERE username = ?',
        (password, username)
    )
    return True


def set_follows(username1, username2):
    """Set username1 to follow username2."""
    connection = get_db()
    connection.execute(
        'INSERT INTO '
        'following (username1, username2) '
        'VALUES (?, ?)',
        (username1, username2)
    )
    return True


def delete_follows(username1, username2):
    """Delete username1 follows username2."""
    connection = get_db()
    connection.execute(
        'DELETE FROM '
        'following '
        'WHERE username1 = ? AND username2 = ?',
        (username1, username2)
    )
    return True


def delete_user(username):
    """Delete user from table."""
    files = set()
    files.add(get_user_photo(username))
    posts = get_user_posts_filename(username)
    print(posts)
    for entry in posts:
        files.add(entry['filename'])
    for file in files:
        path = insta485.app.config["UPLOAD_FOLDER"]/file
        os.remove(path)
    connection = get_db()
    connection.execute(
        'DELETE FROM users '
        'WHERE username = ?',
        (username, )
    )
    return True


def is_following(postid, username):
    """Check if current username is following owner of postid."""
    connection = get_db()
    cur = connection.execute(
        'SELECT owner '
        'FROM posts '
        'WHERE postid = ?',
        (postid, )
    )
    post_owner = cur.fetchone()['owner']
    if post_owner == username:
        return True
    cur = connection.execute(
        'SELECT * '
        'FROM following '
        'WHERE username1 = ? AND username2 = ?',
        (username, post_owner)
    )
    return len(cur.fetchall()) == 1


# ===== POSTS =====
def get_posts(username, limit=10, offset=0, postid_lte=None):
    """Get posts from table by users followed by username."""
    connection = get_db()
    if postid_lte is None:
        cur = connection.execute(
            'SELECT DISTINCT posts.* '
            'FROM posts, following '
            'WHERE (following.username1 = ?'
            'AND posts.owner = following.username2) OR '
            'posts.owner = ? '
            'ORDER BY postid DESC '
            'LIMIT ? OFFSET ?',
            (username, username, limit, offset)
        )
    else:
        cur = connection.execute(
            'SELECT DISTINCT posts.* '
            'FROM posts, following '
            'WHERE ((following.username1 = ?'
            'AND posts.owner = following.username2) OR '
            'posts.owner = ?) AND '
            'posts.postid <= ? '
            'ORDER BY postid DESC '
            'LIMIT ? OFFSET ?',
            (username, username, postid_lte, limit, offset)
        )
    return cur.fetchall()


def get_post_data(postid):
    """Get post data from table."""
    connection = get_db()
    cur = connection.execute(
        'SELECT * '
        'FROM posts '
        'WHERE postid = ?',
        (postid, )
    )
    post = cur.fetchone()
    if post is None:
        flask.abort(404)
    post['filename'] = '/uploads/' + post['filename']
    post['user_filename'] = '/uploads/' + get_user_photo(post['owner'])
    post['comments'] = get_post_comments(postid)
    post['likes'] = get_post_like_count(postid)
    post['time_since_created'] = arrow.get(post['created']).humanize()
    return post


def get_post_filename(postid):
    """Get post filename from table."""
    connection = get_db()
    cur = connection.execute(
        'SELECT filename '
        'FROM posts '
        'WHERE postid = ?',
        (postid, )
    )
    return cur.fetchone()['filename']


def get_post_comments(postid):
    """Get comments for post."""
    connection = get_db()
    cur = connection.execute(
        'SELECT * '
        'FROM comments '
        'WHERE postid = ?',
        (postid, )
    )
    comments = cur.fetchall()
    return comments


def get_post_like_count(postid):
    """Get likes for post."""
    connection = get_db()
    cur = connection.execute(
        'SELECT likeid '
        'FROM likes '
        'WHERE postid = ?',
        (postid, )
    )
    likes = cur.fetchall()
    return len(likes)


def user_like_post(username, postid):
    """Return likeid if user has liked post."""
    connection = get_db()
    cur = connection.execute(
        'SELECT * '
        'FROM likes '
        'WHERE postid = ? AND owner = ?',
        (postid, username)
    )
    data = cur.fetchone()
    if data is None:
        return 0
    return data['likeid']


def create_like(username, postid):
    """Create new like for post."""
    connection = get_db()
    connection.execute(
        'INSERT INTO '
        'likes (owner, postid) '
        'VALUES (?, ?)',
        (username, postid)
    )
    return True


def delete_like(username, postid=None, likeid=None):
    """Delete a like."""
    if postid is not None:
        connection = get_db()
        connection.execute(
            'SELECT * FROM likes '
            'WHERE owner = ? AND postid = ?',
            (username, postid)
        )
        connection.execute(
            'DELETE FROM likes '
            'WHERE owner = ? AND postid = ?',
            (username, postid)
        )

    if likeid is not None:
        connection = get_db()
        cur = connection.execute(
            'SELECT * FROM likes '
            'WHERE likeid = ?',
            (likeid, )
        )
        data = cur.fetchone()
        if data is None:
            return False, 404
        if data['owner'] != username:
            return False, 403

        connection.execute(
            'DELETE FROM likes '
            'WHERE likeid = ?',
            (likeid, )
        )
        return True, 204

    return False, 403


def create_post(username, filename):
    """Create a post."""
    connection = get_db()
    connection.execute(
        'INSERT INTO '
        'posts (filename, owner)'
        'VALUES (?, ?)',
        (filename, username)
    )
    return True


def delete_post(postid, filename):
    """Delete post rom posts."""
    connection = get_db()
    connection.execute(
        'DELETE FROM posts '
        'WHERE postid = ?',
        (postid, )
    )
    path = insta485.app.config["UPLOAD_FOLDER"]/filename
    os.remove(path)
    return True


# ===== Comments =====

def get_comment_owner(commentid):
    """Return the owner of a comment."""
    connection = get_db()
    cur = connection.execute(
        'SELECT owner '
        'FROM comments '
        'WHERE commentid = ?',
        (commentid, )
    )
    return cur.fetchone()


def create_comment(username, postid, text):
    """Update comments for post."""
    connection = get_db()
    connection.execute(
        'INSERT INTO '
        'comments (owner, postid, text) '
        'VALUES (?, ?, ?)',
        (username, postid, text)
    )
    return True


def delete_comment(username, commentid):
    """Delete comment from comments."""
    connection = get_db()
    cur = connection.execute(
        'SELECT * FROM comments '
        'WHERE commentid = ?',
        (commentid, )
    )
    data = cur.fetchone()
    if data is None:
        return False, 404
    if data['owner'] != username:
        return False, 403

    connection = get_db()
    connection.execute(
        'DELETE FROM comments '
        'WHERE commentid = ?',
        (commentid, )
    )
    return True, 204
