$('#forgotPasswordForm').onload(e.preventDefault)
$('#passwordBtn').onclick(function (e) {
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
    showMessage("Message has been delivered",'messageDiv')
    clearMessage('messageDiv',10000)
})


