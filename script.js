function sendMessage(){

let input=document.getElementById("userInput").value;
let chat=document.getElementById("chatbox");

chat.innerHTML += "<p><b>You:</b> "+input+"</p>";

fetch("/get",{
method:"POST",
headers:{
"Content-Type":"application/x-www-form-urlencoded"
},
body:"msg="+encodeURIComponent(input)
})
.then(response=>response.json())
.then(data=>{
chat.innerHTML += "<p><b>Bot:</b> "+data.reply+"</p>";
});

document.getElementById("userInput").value="";
}