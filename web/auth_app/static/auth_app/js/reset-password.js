
$('#forgotPasswordForm').submit(function (e) {
    e.preventDefault() //Модальная форма почему-то перезагружает страницу, самое быстрое решение проблемы
    //Не понимаю почему так происходит. Имею ввиду когда 2 js накидываю, то при нажатии на кнопку страница перезагружается(хотя не должна)
    var form = $(this);
    var resetBtn = form.find('#passwordBtn')
    $.ajax({
        url:'/api/v1/auth/password/reset/',
        type: 'POST',
        data:form.serialize(),
        dataType: 'json',
        success: function(data){
            showMessage(data)
        },
        error: function(xhr){
            var errors = xhr.responseJSON; //debug errors 
            showMessage(errors.detail)
        }
    })
})

function showMessage(message) {
    const messageDiv = document.getElementById('messageDiv')
    const tag = document.createElement("H1")
    const informationContent = document.createTextNode(message)

    tag.appendChild(informationContent)
    messageDiv.appendChild(tag)
}
