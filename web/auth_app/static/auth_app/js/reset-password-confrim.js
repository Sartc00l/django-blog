

$(function () {
    const queryParams = new URLSearchParams(window.location.search)
    const uid = queryParams.get('uid')
    const token = queryParams.get('token')



    ValidateToken(uid,token)

    $('#resetPasswordBtn').click(function(e){
        e.preventDefault();
        const password1 = $('#password1').val()
        const password2 =$('#password2').val()
        showMessage("btn click")
        changePassword(password1,password2,uid,token)
    })
});
const ValidateToken = (uid,token)=>{
    const tokenData = {
        'uid':uid,
        'token':token
    }

    $.ajax({
        url:'/api/v1/auth/password/reset/validate',
        type: 'POST',
        data: JSON.stringify(tokenData),
        contentType:'application/json',
        success:function(response){
            showPasswordForm()
        },
        error: function(xhr){
            var errors = xhr.responseJSON
            if(errors && errors.detail){
                showMessage(errors.detail)
            }
        }
    })
}

const changePassword=(password1,password2,uid,token)=>{
    if(!password1||!password2 && password1.length < 7){
        showMessage("Please fill empty fields")
        showMessage(password1,password2)
        return
    }
    if (password1 !== password2 && password1.length < 7){
        showMessage("Passwords don't match")
        return
    }
    const passwordData={
        'password_1':password1,
        'password_2':password2,
        'uid':uid,
        'token':token
    }

    $.ajax({
        url: '/api/v1/auth/password/reset/confirm/',
        type: 'POST',
        data: JSON.stringify(passwordData),
        contentType:'application/json',
        success: function (response) {
            showMessage("Password has been changed!")
            showMessage("You will be redirected to the login page")
            timer(10)
        },
        error: function (xhr) {
            var errors = xhr.responseJSON
            if(errors && errors.detail){
                showMessage(errors.detail)
            }
        }
    })

}

function showPasswordForm(){
    document.getElementById('PasswordResetForm').style.display='block'
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

