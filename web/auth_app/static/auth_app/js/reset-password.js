
$('#forgotPasswordForm').submit(function (e) {
    var form = $(this);
    var resetBtn = form.find('#passwordBtn')
    $.ajax({
        url:'/api/v1/auth/password/reset/',
        type: 'POST',
        data:form.serialize(),
        dataType: 'json',
        success: function(data){
            console.log(data)
        },
        error: function(xhr){
            var errors = xhr.responseJSON;
            console.log(errors)
        }
    })
})
