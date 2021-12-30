
function show (message, user) {
    let el = document.createElement("div")
    el.innerHTML = `<strong>${user}</strong> ${message}`
    document.querySelector("div.chatbox>div.messages").appendChild(el)
}

document.querySelector("div.chatbox input").addEventListener('keyup', function (e) {
    if (e.key === 'Enter' || e.keyCode === 13) {
        if (e.target.value.trim() != "") {
            ws.send(`MESSAGE: ${e.target.value}`)
            e.target.value = ""
            setTimeout(()=>{document.querySelector("div.chatbox>div.messages").scrollTo(0, 1000)}, 1)
        }
    }
});
