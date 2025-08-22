$(function () {
    verifyEmail()
});
function verifyEmail() {
    const urlsParams = new URLSearchParams(window.location.search)
    const data = {
        key: urlsParams.get('key')
    }
    $.ajax({
        url: '/api/v1/auth/sign-up/verify/',
        type: 'POST',
        data: data,
        success: function () {
            showMessage("Confirmed!")
        },
        error: function (xhr) {
            var errors = xhr.responseJSON;
            if (errors) {
                showMessage(errors.detail)
            }
        }
    })

}


function showMessage(message) {
    const messageDiv = document.getElementById('messageDiv')
    const tag = document.createElement("H1")
    const informationContent = document.createTextNode(message)

    tag.appendChild(informationContent)
    messageDiv.appendChild(tag)

    timer(10)
}
function timer(seconds) {
    const timer = setInterval(() => { document.getElementById('timer').textContent = seconds < 0 
        ? window.location.href = "../login" : seconds--; },1000)
}

