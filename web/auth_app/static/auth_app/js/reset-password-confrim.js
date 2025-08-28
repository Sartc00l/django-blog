$(function () {
    $('#resetPasswordBtn').click(function(e){
        changePassword()
    })
});
function changePassword() {
    $.ajax({
        url: '/api/v1/auth/password/reset/confirm/',
        type: 'POST',
        data: data,
        success: function () {
            showMessage("Password has been changed!")
            showMessage("You will be redirected to the login page")
            timer(10)
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

}

function timer(seconds) {
    const timer = setInterval(() => { document.getElementById('timer').textContent = seconds < 0 
        ? window.location.href = "../login" : seconds--; },1000)
}

