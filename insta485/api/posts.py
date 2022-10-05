"""REST API for posts."""
import flask
import insta485
from insta485 import model
import pprint


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
  """Return post on postid.
  Example:
  {
    "created": "2017-09-28 04:33:28",
    "imgUrl": "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
    "owner": "awdeorio",
    "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
    "ownerShowUrl": "/users/awdeorio/",
    "postShowUrl": "/posts/1/",
    "url": "/api/v1/posts/1/"
  }
  """
  
  if 'login' not in flask.session:
    flask.abort(403)
  login_user = flask.session['login']

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