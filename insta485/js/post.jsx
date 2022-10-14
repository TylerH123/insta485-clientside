import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import moment from "moment/moment";

export default function Post(props) {
  const [postDetails, setPostDetails] = useState(null);
  const [postLiked, setPostLiked] = useState(false);
  const [postNumLikes, setPostNumLikes] = useState(0);
  const [commentText, setCommentText] = useState('');

  const getPostData = () => {
    const { url } = props;

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
  }

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

  const submitComment = (e) => {
    e.preventDefault();
    fetch(`/api/v1/comments/?postid=${postDetails.postid}`, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: commentText }),
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        const newDetails = { ...postDetails };
        newDetails.comments = [...newDetails.comments, data];
        setPostDetails(newDetails);
      })
      .catch((error) => {
        console.log(error);
      });
    setCommentText('');
  }

  const deleteComment = (commentid) => {
    fetch(`/api/v1/comments/${commentid}/`, {
      method: "DELETE",
      credentials: "same-origin",
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
      })
      .then(() => {
        const newDetails = { ...postDetails };
        const commentInd = newDetails.comments.findIndex(x => x.commentid === commentid);
        newDetails.comments.splice(commentInd, 1);
        setPostDetails(newDetails);
      })
      .catch((error) => {
        console.log(error);
      });
  }

  // Get data for post, runs before render
  useEffect(() => {
    getPostData();
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
          onDoubleClick={postLiked ? null : updatePostLiked}
        />
        <div className="post_stats">
          <div>
            {postNumLikes} {postNumLikes === 1 ? "like" : "likes"}
          </div>
          {postLiked ? (
            <button
              className="btn btn-sm btn-danger like-unlike-button"
              type="button"
              onClick={updatePostLiked}
            >
              Unlike
            </button>
          ) : (
            <button
              className="btn btn-sm btn-primary like-unlike-button"
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
              {
                comment.lognameOwnsThis ?
                  <button type="button" className="btn btn-sm btn-danger delete-comment-button" onClick={() => { deleteComment(comment.commentid) }}>
                    Delete
                  </button> : null
              }

            </div>
          ))}
          <form className="comment-form" onSubmit={(e) => submitComment(e)}>
            <input
              className="comment_input"
              type="text"
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
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
