import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import moment from "moment/moment";

export default function Post(props) {
  const { url } = props;
  const [postDetails, setPostDetails] = useState(null);
  const [postLiked, setPostLiked] = useState(false);
  const [commentText, setCommentText] = useState('');
  const [postNumLikes, setPostNumLikes] = useState(0);

  const updatePostLiked = () => {
    if (postLiked) {
      fetch(postDetails.likes.url, {
        method: "DELETE",
        credentials: "same-origin",
      })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
        })
        .then(() => {
          setPostLiked(false);
          setPostNumLikes(postNumLikes - 1);
        })
        .catch((error) => {
          console.log(error);
        });
    } else {
      fetch(`/api/v1/likes/?postid=${postDetails.postid}`, {
        method: "POST",
        credentials: "same-origin",
      })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          setPostLiked(true);
          setPostNumLikes(postNumLikes + 1);

          const newDetails = { ...postDetails };
          newDetails.likes.url = data.url;
          setPostDetails(newDetails);
        })
        .catch((error) => {
          console.log(error);
        });
    }
  };

  // http -a awdeorio:password \
  // POST \
  // "http://localhost:8000/api/v1/comments/?postid=3" \
  // text='Comment sent from httpie'

  const submitComment = (e) => {
    e.preventDefault();
    fetch(`/api/v1/comments/?postid=${postDetails.postid}`, {
      method: "POST",
      credentials: "same-origin",
      body: JSON.stringify({ 'text': commentText }),
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
      });
  }

  // Get data for post, runs before render
  useEffect(() => {
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        setPostDetails(data);
        setPostLiked(data.likes.lognameLikesThis);
        setPostNumLikes(data.likes.numLikes);
      })
      .catch((error) => {
        console.log(error);
      });
  }, [props]);

  return (
    postDetails && (
      <div className="post">
        <div className="post_header">
          <a href={`/users/${postDetails.owner}/`}>
            <div className="post_header_left">
              <img
                className="pfp"
                alt={postDetails.owner}
                src={postDetails.ownerImgUrl}
              />
              <div className="username">{postDetails.owner}</div>
            </div>
          </a>
          <a href={`/posts/${postDetails.postid}/`}>
            <div className="timestamp">
              {moment.utc(postDetails.created).fromNow()}
            </div>
          </a>
        </div>
        <img
          className="photo"
          alt={postDetails.imgUrl}
          src={postDetails.imgUrl}
        />
        <div className="post_stats">
          <div>
            {postNumLikes} {postNumLikes === 1 ? "like" : "likes"}
          </div>
          {postLiked ? (
            <button
              className="btn btn-sm btn-danger"
              type="button"
              onClick={updatePostLiked}
            >
              Unlike
            </button>
          ) : (
            <button
              className="btn btn-sm btn-primary"
              type="button"
              onClick={updatePostLiked}
            >
              Like
            </button>
          )}
        </div>
        <div className="comment_section">
          {postDetails.comments.map((comment) => (
            <div className="comment" key={`comment-${comment.commentid}`}>
              <a href={comment.ownerShowUrl}>
                <div className="username">{comment.owner}</div>
              </a>
              <p>{comment.text}</p>
            </div>
          ))}
          <form className="comment-form" onSubmit={(e) => submitComment(e)}>
            <input
              className="comment_input"
              type="text"
              name="text"
              onChange={(e) => { setCommentText(e.target.value); console.log(commentText); }}
              required
            />
          </form>
        </div>
      </div>
    )
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};
