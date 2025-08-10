$(function (){
    verifyEmail()
});
function verifyEmail(){
    const urlsParams = new  URLSearchParams(window.location.search)
    const data = {
        key: urlsParams.get('key')
    }
    console.log(data)
    $.ajax({
        url:'/api/v1/auth/sign-up/verify/',
        type:'POST',
        data:data,
        success:successVerifyEmail,
        error:errorVerifyEmail
    })

}

function successVerifyEmail(data){
    console.log('success ',data)
}
function errorVerifyEmail(data){
    console.log('error ',data)
}