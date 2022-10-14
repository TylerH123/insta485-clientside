"""REST API for posts."""
import flask
import insta485
from insta485 import model


@insta485.app.route('/api/v1/')
def get_api():
    """Get api routes."""
    context = {
        'comments': '/api/v1/comments/',
        'likes': '/api/v1/likes/',
        'posts': '/api/v1/posts/',
        'url': '/api/v1/'
    }
    return flask.jsonify(**context), 200


@insta485.app.route('/api/v1/posts/')
def get_posts():
    """Get posts."""
    if 'login' in flask.session:
        login_user = flask.session['login']
    else:
        login_user = auth()

    postid_lte = flask.request.args.get('postid_lte', default=None, type=int)
    size = flask.request.args.get('size', default=10, type=int)
    page = flask.request.args.get('page', default=0, type=int)
    posts_data = model.get_posts(login_user, limit=size,
                                 offset=page*size, postid_lte=postid_lte)

    if size < 0 or page < 0:
        flask.abort(400)

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
        postid_lte = postid_lte or posts_object[0]["postid"]
        ext = f'?size={size}&page={page + 1}&postid_lte={postid_lte}'
        next_link = f'/api/v1/posts/{ext}'
    if len(flask.request.args):
        url = flask.request.full_path
    else:
        url = flask.request.path
    context = {
        'next': next_link,
        'results': posts_object,
        'url': url
    }
    return flask.jsonify(**context), 200


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    """Get a singular post."""
    if 'login' in flask.session:
        login_user = flask.session['login']
    else:
        login_user = auth()

    post_data = model.get_post_data(postid_url_slug)

    comments_list = []
    for item in post_data['comments']:
        comment = {
            'commentid': item['commentid'],
            'lognameOwnsThis': login_user == item['owner'],
            'owner': item['owner'],
            'ownerShowUrl': f'/users/{ item["owner"] }/',
            'text': item['text'],
            'url': f'/api/v1/comments/{ item["commentid"] }/'
        }
        comments_list.append(comment)

    user_like_id = model.user_like_post(login_user, postid_url_slug)
    if not user_like_id:
        like_url = None
    else:
        like_url = f'/api/v1/likes/{user_like_id}/'
    context = {
        'comments': comments_list,
        'comments_url': f'/api/v1/comments/?postid={postid_url_slug}',
        'created': post_data['created'],
        'imgUrl': post_data['filename'],
        'likes': {
            'numLikes': post_data['likes'],
            'lognameLikesThis': bool(user_like_id),
            'url': like_url
        },
        'owner': post_data['owner'],
        'ownerImgUrl': post_data['user_filename'],
        'ownerShowUrl': f'/users/{ post_data["owner"] }/',
        'postShowUrl': f'/posts/{ postid_url_slug }/',
        'postid': post_data['postid'],
        'url': f'/api/v1/posts/{ postid_url_slug }/'
    }
    return flask.jsonify(**context), 200


@insta485.app.route('/api/v1/likes/', methods=['POST'])
@insta485.app.route('/api/v1/likes/<int:likeid_url_slug>/', methods=['DELETE'])
def post_likes(likeid_url_slug=None):
    """POST or DELETE like."""
    if 'login' in flask.session:
        login_user = flask.session['login']
    else:
        login_user = auth()
    if flask.request.method == 'POST':
        postid = flask.request.args.get('postid')
        if postid is None:
            flask.abort(404)

        response = 200
        if not model.user_like_post(login_user, postid):
            model.create_like(login_user, postid)
            response = 201

        likeid = model.user_like_post(login_user, postid)
        context = {
            'likeid': likeid,
            'url': '/api/v1/likes/' + str(likeid) + '/'
        }
        return flask.jsonify(**context), response
    success, response = model.delete_like(login_user, likeid=likeid_url_slug)
    if not success:
        flask.abort(response)

    return '', response


@insta485.app.route('/api/v1/comments/', methods=['POST'])
@insta485.app.route('/api/v1/comments/<int:commentid_url_slug>/',
                    methods=['DELETE'])
def post_comments(commentid_url_slug=None):
    """POST or DELETE comment."""
    if 'login' in flask.session:
        login_user = flask.session['login']
    else:
        login_user = auth()

    if flask.request.method == 'POST':
        postid = flask.request.args.get('postid')
        if postid is None:
            flask.abort(404)

        if 'text' not in flask.request.json:
            flask.abort(400)

        text = flask.request.json.get('text')
        if text is None:
            flask.abort(400)

        model.create_comment(login_user, postid, text)
        commentid = model.get_last_insert_rowid()

        context = {
            'commentid': commentid,
            'lognameOwnsThis': True,
            'owner': login_user,
            'ownerShowUrl': f'/users/{login_user}/',
            'text': text,
            'url': f'/api/v1/comments/{commentid}/'
        }
        return flask.jsonify(**context), 201

    success, response = model.delete_comment(login_user, commentid_url_slug)
    if not success:
        flask.abort(response)

    return '', response


def auth():
    """Authenticate user."""
    if flask.request.authorization:
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if username is None or password is None or \
           username == '' or password == '':
            flask.abort(403)
        data = model.get_user_data(username)
        if data is None:
            flask.abort(403)
        salt = data['password'].split('$')[1]
        hashed_pass = model.hash_password(password, salt)
        if data['password'] != hashed_pass:
            flask.abort(403)
        return username
    return flask.abort(403)
