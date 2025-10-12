const express = require("express");
const app = express();
const port = 3000;


app.use(express.urlencoded({extended:true}));
app.use(express.static('public'));
app.set("view engine", "ejs");


let todos = [];
app.get("/", (req,res) =>{
    res.render("index", {todos : todos})
});

app.post("/addTask", (req,res) => {
    todos.push(req.body.add);
    res.redirect("/")
});

app.post("/deleteTask", (req,res) => {
    const del = req.body.del;
    todos.splice(del,1);
    res.redirect("/")
})


app.listen(port, () => {
    console.log(`APP Listening at http://localhost:${port}`);
});