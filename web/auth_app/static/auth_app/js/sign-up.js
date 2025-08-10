$(document).ready(function () {
  $('#signUpForm').submit(function (e) {
    e.preventDefault();
    var form = $(this);
    var submitButton = form.find('.signup-btn');


    submitButton.prop('disabled', true).text('Processing...');

    $.ajax({
      url: form.attr('action'),
      type: 'POST',
      data: form.serialize(),
      dataType: 'json',
      success: function (data) {

        showAlert('success', data.detail);
        form[0].reset();

      },
      error: function (xhr) {
        var errors = xhr.responseJSON;
        clearErrors();

        if (errors) {

          handleFormErrors(errors);
        } else {

          showAlert('danger', 'Server error. Please try again later.');
        }
      },
      complete: function () {
        submitButton.prop('disabled', false).text('Create my account');
      }
    });
  });

  function clearErrors() {
    $('.form-group').removeClass('has-error');
    $('.help-block.error').remove();
    $('.alert-dismissible').remove();
  }

  function handleFormErrors(errors) {

    $.each(errors, function (field, messages) {
      var inputGroup = $('[name="' + field + '"]').closest('.form-group');
      if (inputGroup.length) {
        inputGroup.addClass('has-error');
        inputGroup.append('<div class="help-block error">' + messages.join(' ') + '</div>');
      } else {

        showAlert('danger', messages.join(' '));
      }
    });
  }

  function showAlert(type, message) {
    var alertClass = 'alert alert-' + type + ' alert-dismissible';
    var alertHtml = '<div class="' + alertClass + '" role="alert">' +
      '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
      '<span aria-hidden="true">&times;</span>' +
      '</button>' +
      message +
      '</div>';

    $('#alertContainer').html(alertHtml);


    setTimeout(function () {
      $('.alert').alert('close');
    }, 100000);
  }
});