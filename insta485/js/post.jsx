import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

export default function Post(props) {
    const [imgUrl, setImgUrl] = useState("");
    const [owner, setOwner] = useState("");

    useEffect(() => {
        // This line automatically assigns this.props.url to the const variable url
        const { url } = props;
        // Call REST API to get the post's information

        let posts;
        fetch(url, { credentials: "same-origin" })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                posts = data.results
            })
            .catch((error) => console.log(error));


    });



    return (
        <div className="post">
            <img src={imgUrl} alt="post_image" />
            <p>{owner}</p>
        </div>
    )
}

Post.propTypes = {
    url: PropTypes.string.isRequired,
};