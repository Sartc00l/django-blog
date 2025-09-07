
function showMessage(message,messageBlock) {
    const messageDiv = document.getElementById(messageBlock)
    const tag = document.createElement("H1")
    const informationContent = document.createTextNode(message)

    tag.appendChild(informationContent)
    messageDiv.appendChild(tag)

    clearMessage(messageBlock,)
}

function clearMessage(messageSpace,seconds){
    const timer = setInterval(()=>{
        document.getElementById(messageSpace).textContent = ''
    },seconds)
}

function timer(seconds) {
    const timer = setInterval(() => { document.getElementById('timer').textContent = seconds < 0 
        ? window.location.href = "../login" : seconds--; },seconds)
}

