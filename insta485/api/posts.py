"""REST API for posts."""
import flask
import insta485
from insta485 import model
import pprint


@insta485.app.route('/api/v1/')
def get_api():
    context = {
        'comments': '/api/v1/comments/',
        'likes': '/api/v1/likes/',
        'posts': '/api/v1/posts/',
        'url': '/api/v1/'
    }
    return flask.jsonify(**context)


@insta485.app.route('/api/v1/posts/')
def get_posts():
    if 'login' in flask.session:
        login_user = flask.session['login']
    else:
        auth()

    postid_lte = flask.request.args.get('postid_lte', default=None, type=int)
    size = flask.request.args.get('size', default=10, type=int)
    page = flask.request.args.get('page', default=0, type=int)
    posts_data = model.get_posts(login_user, limit=size,
                                 offset=page*size, postid_lte=postid_lte)

    posts_object = []
    for item in posts_data:
        post = {
            'postid': item['postid'],
            'url': f'/api/v1/posts/{ item["postid"] }/'
        }
        posts_object.append(post)

    if len(posts_object) < size:
        next_link = ''
    else:
        next_link = f'/api/v1/posts/?size={size}&page={page + 1}&postid_lte={postid_lte or posts_object[0]["postid"]}'

    context = {
        'next': next_link,
        'results': posts_object,
        'url': flask.request.full_path if len(flask.request.args) else flask.request.path
    }
    return flask.jsonify(**context)


# @insta485.app.route()
# def get_page():
#   if 'login' not in flask.session:
#     flask.abort(403)
#   login_user = flask.session['login']

#   context = {}

#   return flask.jsonify(**context)


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    if 'login' in flask.session:
        login_user = flask.session['login']
    else:
        auth()

    post_data = model.get_post_data(postid_url_slug)

    comments_object = []
    for item in post_data['comments']:
        comment = {
            'commentid': item['commentid'],
            'lognameOwnsThis': login_user == item['owner'],
            'owner': item['owner'],
            'ownerShowUrl': f'/users/{ item["owner"] }/',
            'text': item['text'],
            'url': f'/api/v1/comments/{ item["commentid"] }/'
        }
        comments_object.append(comment)

    context = {
        'comments': comments_object,
        'comments_url': f'/api/v1/comments/?postid={postid_url_slug}',
        'created': post_data['created'],
        'imgUrl': post_data['filename'],
        'likes': {
            'lognameLikesThis': model.user_like_post(login_user, postid_url_slug),
            'numLikes': post_data['likes'],
            'url': None,
        },
        'owner': post_data['owner'],
        'ownerImgUrl': post_data['user_filename'],
        'ownerShowUrl': f'/users/{ post_data["owner"] }/',
        'postShowUrl': f'/posts/{ postid_url_slug }/',
        'postid': post_data['postid'],
        'url': f'/api/v1/posts/{ postid_url_slug }/'
    }
    return flask.jsonify(**context)


@insta485.app.route('/api/v1/likes/', methods=['POST'])
def post_likes():
    if 'login' in flask.session:
        login_user = flask.session['login']
    else:
        login_user = flask.request.authorization['username']
        auth(login_user)

    postid = flask.request.args.get('postid')
    if postid is None:
        flask.abort(404)

    context = {
        'postid': int(postid),
        'url': '/api/v1/likes/' + postid + '/'
    }

    if not model.user_like_post(login_user, postid):
        response = 200
    else:
        model.update_likes(True, login_user, postid)
        response = 201

    return flask.jsonify(**context), response


def auth(username):
    password = flask.request.authorization['password']
    if username is None or password is None or \
       username == '' or password == '':
        flask.abort(403)
    data = model.get_user_data(username)
    if data is None:
        flask.abort(403)
    hashed_pass = model.hash_password(password,
                                      data['password'].split('$')[1])
    if data['password'] != hashed_pass:
        flask.abort(403)
