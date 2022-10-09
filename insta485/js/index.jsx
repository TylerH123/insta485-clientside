import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import Post from "./post";

export default function Index(props) {
  const [postsToRender, setPostsToRender] = useState([]);

  useEffect(() => {
    const { url } = props;

    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        setPostsToRender(data.results);
      })
      .catch((error) => console.log(error));
  }, [props]);

  return (
    <div id="site_body">
      <div id="feed">
        {postsToRender.map((post) => (
          <Post key={`post-${post.postid}`} url={post.url} isPostPage={false} />
        ))}
      </div>
    </div>
  );
}

Index.propTypes = {
  url: PropTypes.string.isRequired,
};
