const express = require("express");
const app = express();
const PORT = 3000;

// Serve static files from the 'public' folder
app.use(express.static("public"));

app.get("/", (req, res) => {
    res.sendFile(__dirname + "/public/index.html");
});

app.listen(PORT, () => {
    console.log(`Server is running at http://localhost:${PORT}`);
});
