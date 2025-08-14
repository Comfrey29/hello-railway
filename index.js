const express = require("express");
const app = express();

app.get("/", (req, res) => {
  res.send("Hello from Railway 🚂");
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Servidor escoltant al port ${port}`);
});
