import React, { useState, useEffect, useRef } from "react";
import PropTypes from "prop-types";
import InfiniteScroll from "react-infinite-scroll-component";

import Post from "./post";

export default function Index(props) {
  const [postsToRender, setPostsToRender] = useState([]);
  const nextPostsUrl = useRef('');

  useEffect(() => {
    const { url } = props;

    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        setPostsToRender(data.results);
        nextPostsUrl.current = data.next;
      })
      .catch((error) => console.log(error));
  }, [props]);

  const getNextData = () => {
    fetch(nextPostsUrl.current, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        setPostsToRender([...postsToRender, ...data.results]);
      })
      .catch((error) => console.log(error));
  }

  return (
    <div id="site_body">
      <InfiniteScroll
        id="feed"
        dataLength={postsToRender.length}
        next={getNextData}
        loader={<h4>Loading...</h4>}
        endMessage={
          <p style={{ textAlign: 'center' }}>
            <b>Yay! You have seen it all</b>
          </p>
        }
      >
        {postsToRender.map((post) => (
          <Post key={`post-${post.postid}`} url={post.url} />
        ))}
      </InfiniteScroll>
    </div>
  );
}

Index.propTypes = {
  url: PropTypes.string.isRequired,
};
