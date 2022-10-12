import React, { useState, useEffect, useRef } from "react";
import PropTypes from "prop-types";
import InfiniteScroll from "react-infinite-scroll-component";

import Post from "./post";

export default function Index(props) {
  const [postsToRender, setPostsToRender] = useState([]);
  const nextPostsUrl = useRef('');

  useEffect(() => {
    const { url } = props;

    fetch(`${url}?size=1`, { credentials: "same-origin" })
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
    console.log('reached');
    fetch(nextPostsUrl.current, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        setPostsToRender([...postsToRender, ...data.results]);
        nextPostsUrl.current = data.next;
      })
      .catch((error) => console.log(error));
  }

  return (
    <div id="site_body">
      <InfiniteScroll
        id="feed"
        dataLength={postsToRender.length}
        next={getNextData}
        hasMore={nextPostsUrl.current !== ''}
        loader={
          <h5 style={{ textAlign: 'center' }}>
            Loading...
          </h5>
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
