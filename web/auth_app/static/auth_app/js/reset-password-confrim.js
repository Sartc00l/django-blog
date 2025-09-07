

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
        showMessage("Please fill empty fields",'messageDiv')
        showMessage(`password 1 ${password1} \npassword 2:${password2}`,'messageDiv')
        return
    }
    if (password1 !== password2 && password1.length < 7){
        showMessage("Passwords don't match",'messageDiv')
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
            showMessage("Password has been changed!",'messageDiv')
            showMessage("You will be redirected to the login page",'messageDiv')
            timer(10)
        },
        error: function (xhr) {
            var errors = xhr.responseJSON
            if(errors && errors.detail){
                showMessage(errors.detail,'messageDiv')
            }
        }
    })

}

