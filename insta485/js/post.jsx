import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

export default function Post(props) {
    const [postsToRender, setPostsToRender] = useState([]);
    // const [imgUrl, setImgUrl] = useState("");
    // const [owner, setOwner] = useState("");

    useEffect(() => {
        // This line automatically assigns this.props.url to the const variable url
        // Call REST API to get the post's information

        const { url } = props;

        let resultsPosts;
        fetch(url, { credentials: "same-origin" })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                setPostsToRender(data.results)
                resultsPosts = data.results
            })
            .then(() => {
                const posts = resultsPosts.map((post) => {
                    let temp;
                    fetch(`/api/v1/posts/${post.postid}/`, { credentials: "same-origin" })
                        .then((response) => {
                            if (!response.ok) throw Error(response.statusText);
                            return response.json();
                        })
                        .then((data) => { temp = data })
                        .catch((error) => console.log(error));

                    return temp;
                });
            })
            .catch((error) => console.log(error));



        // setPostsToRender(posts);
    }, [props]);

    return (
        <div>
            {JSON.stringify(postsToRender)}
        </div>
        // <div className="post">
        //     {/* <img src={imgUrl} alt="post_image" />
        //     <p>{owner}</p> */}
        // </div>
    )
}

Post.propTypes = {
    url: PropTypes.string.isRequired,
};