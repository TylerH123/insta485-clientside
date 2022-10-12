import React from "react";
import { createRoot } from "react-dom/client";

import Index from ".";

const root = createRoot(document.getElementById("reactEntry"));

root.render(<Index url="/api/v1/posts/" />);