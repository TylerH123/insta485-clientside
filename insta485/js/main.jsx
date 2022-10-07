import React from "react";
import { createRoot } from "react-dom/client";
import Post from "./post";

const root = createRoot(document.getElementById("reactEntry"));

root.render(<Post url="/api/v1/posts/1/" />);