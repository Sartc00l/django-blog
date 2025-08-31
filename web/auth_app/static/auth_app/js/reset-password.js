
$('#forgotPasswordForm').submit(function (e) {
    e.preventDefault()
    var form = $(this);
    var resetBtn = form.find('#passwordBtn')
    $.ajax({
        url:'/api/v1/auth/password/reset/',
        type: 'POST',
        data:form.serialize(),
        dataType: 'json',
    })
    $('#pwdModal').modal('hide');
    showMessage("Message has been delivered")
})

function showMessage(message) {
    const messageDiv = document.getElementById('messageDiv')
    const tag = document.createElement("H1")
    const informationContent = document.createTextNode(message)

    tag.appendChild(informationContent)
    messageDiv.appendChild(tag)
}
