
var number, name, phone_number, code, email;
var reset = function(){
	$('#sendCode').removeAttr('disabled');
	$('#authenticationComplete').attr('disabled', true);
	$('#authenticationCode').attr('disabled', true);
	$('#authenticationCheck').attr('disabled', true);
	$('#loading_img').hide();
	number = $('#inputNumber').val();
	name = $('#inputName').val();
	tmp = $('#inputPhoneNumber').val();
	if (tmp.length == 11){
		phone_number = tmp.slice(0, 3) + '-' + tmp.slice(3, 7) + '-' + tmp.slice(7, 11);
		$('#inputPhoneNumber').val(phone_number);
	}
	phone_number = $('#inputPhoneNumber').val();
	code = '';
};

function validateEmail(email) {
	var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
	return re.test(email);
}

var email_reset = function(){
	$('#email_loading_img').hide();
	$('#emailAddress').html(email);
	$('#sendMail').removeAttr('disabled');
	$('#verifyCode').attr('disabled', true);
	$('#verifyCheck').attr('disabled', true);
}

$('#emailButton').click(function(){
	// 메일인증 버튼 클릭
	email = $('#inputEmail').val();
	if (!validateEmail(email)){
		alert('올바르지 않은 이메일 주소입니다.');
		return false;
	}
	email_reset();
});

$('#sendMail').click(function(){
	// 인증 메일 보내기 클릭
	$('#sendMail').attr('disabled', true);
	$('#email_loading_img').show();
	$.ajax({
		url: '/ajax/members/send_verify_email/',
		type: 'post',
		data: {
			email: email,
			csrfmiddlewaretoken: csrf_token
		},
		success: function(rsp){
			if (rsp == 'joined'){
				alert('이미 가입된 이메일 입니다.');
			}else{
				alert('메일을 성공적으로 보냈습니다.');
				$('#email_loading_img').hide();
				$('#sendMail').val('다시 발송');
				$('#verifyCode').removeAttr('disabled');
				$('#verifyCheck').removeAttr('disabled');
				$('#sendMail').removeAttr('disabled');
			}
		}
	});
});

$('#verifyCheck').click(function(){
	var verify_code = $('#verifyCode').val();
	$.ajax({
		url: '/ajax/members/check_verify_code/',
		type: 'post',
		data: {
			email: email,
			code: verify_code,
			csrfmiddlewaretoken: csrf_token
		},
		success: function(rsp){
			if (rsp == 'yes'){
				alert('메일 인증이 완료되었습니다.');
				$('#post-email').val(email);
				$('#emailModal').modal('hide');
				$('#emailButton').attr('disabled', true);
				$('#inputEmail').attr('disabled', true);
				$('button[type="submit"]').removeAttr('disabled');
			}else{
				alert('올바른 인증 코드가 아닙니다.');
			}
		}
	});
});

$('#duplicateButton').click(function(){
	// 중복확인 버튼 클릭
	$.ajax({
		url: '/ajax/members/username_duplication_check/',
		type: 'post',
		data: {
			username: $('#inputUsername').val(),
			csrfmiddlewaretoken: csrf_token
		},
		success: function(rsp){
			if (rsp == 'exists'){
				alert('사용자명이 중복됩니다.');
			}
			else{
				if (confirm('사용 가능한 사용자명입니다. 사용하시겠습니까?')){
					$('#post-username').val($('#inputUsername').val());
					$('#inputUsername').attr('disabled', true);
					$('#duplicateButton').attr('disabled', true);
					$('#emailButton').removeAttr('disabled');
				}
			}
		}
	});
});

$('#authenticateButton').click(function(){
	// 본인 인증 클릭
	if ($('#inputNumber').val() == '' || $('#inputName').val() == '' || $('#inputPhoneNumber').val() == ''){
		$('#auth_alert_message').html('학번, 이름, 연락처 중 빈 칸이 있습니다.');
		$('#auth_alert').show(400);
		return false;
	}
	if ($('#inputNumber').val().length != 10){
		$('#auth_alert_message').html('학번이 올바르지 않습니다.');
		$('#auth_alert').show(400);
		return false;
	}
	$('#auth_alert').hide();
	reset();
	$('#myNumber').html(number);
	$('#myName').html(name);
	$('#myPhoneNumber').html(phone_number);
});

$('#sendCode').click(function(){
	// 인증 번호 보내기 클릭
	$('#sendCode').attr('disabled', true);
	$('#loading_img').show();
	$.ajax({
		url: '/ajax/members/make_security/',
		type: 'post',
		data: {
			number: number,
			name: name,
			phone_number: phone_number,
			csrfmiddlewaretoken: csrf_token
		},
		success: function(rsp){
			$('#loading_img').hide();
			if (rsp == 'unknown'){
				alert('올바르지 않은 학번/이름/연락처 조합입니다. 포털에 등록된 연락처를 기입해주세요.');
				$('#authenticateModal').modal('hide');
			}
			else if (rsp == 'exist'){
				alert('이미 가입되어있습니다.');
				$('#authenticateModal').modal('hide');
			}
			else if (rsp == 'error'){
				alert('문자보내는데 에러가 발생했습니다.');
				$('#sendCode').removeAttr('disabled');
				$('#sendCode').val('다시 발송');
			}
			else if (rsp == 'too many'){
				alert('연속된 3분에 최대 3개의 문자를 보낼 수 있습니다.');
				$('#sendCode').removeAttr('disabled');
				$('#sendCode').val('다시 발송');
			}
			else{
				alert(phone_number+'로 본인 인증 번호 문자를 발송하였습니다.');
				$('#sendCode').removeAttr('disabled');
				$('#sendCode').val('다시 발송');
				$('#authenticationCode').removeAttr('disabled');
				$('#authenticationCheck').removeAttr('disabled');
			}
		}
	});
});

$('#authenticationCheck').click(function(){
	// 인증 확인 버튼 클릭
	code = $('#authenticationCode').val();
	$.ajax({
		url: '/ajax/members/code_check/',
		type: 'post',
		data: {
			number: number,
			name: name,
			phone_number: phone_number,
			code: code,
			csrfmiddlewaretoken: csrf_token
		},
		success: function(rsp){
			if (rsp == 'wrong'){
				alert('틀렸습니다');
			}
			else if (rsp == 'unknown'){
				alert('알 수 없는 문제가 발생했습니다.');
			}
			else{
				alert('본인 인증이 완료되었습니다.');
				$('#post-code').val(code);
				$('#post-number').val(number);
				$('#post-name').val(name);
				$('#post-phone_number').val(phone_number);
				$('#inputNumber').attr('disabled', true);
				$('#inputName').attr('disabled', true);
				$('#inputPhoneNumber').attr('disabled', true);
				$('#authenticateButton').attr('disabled', true);
				$('#authenticateModal').modal('hide');
				$('#inputUsername').removeAttr('disabled');
				$('#duplicateButton').removeAttr('disabled');
			}
		}
	});
});

$('button[type="submit"]').click(function(){
	if ($('input[name="must_be_yes"]:checked').val() != "yes"){
		$('#privacy_alert').show(400);
		return false;
	}
	if ($('#inputPassword').val() != $('#inputPasswordConfirm').val()){
		$('#password_alert').show(400);
		return false;
	}
});

$('.alert .close').click(function(){
	$(this).parent().hide(400);
	return false;
});

$('.toggle-content').click(function(){
	if ($('.toggle-icon').hasClass('glyphicon-menu-down')){
		$('.toggle-icon').removeClass('glyphicon-menu-down');
		$('.toggle-icon').addClass('glyphicon-menu-up');
		$('.content').show(400);
	}else{
		$('.toggle-icon').removeClass('glyphicon-menu-up');
		$('.toggle-icon').addClass('glyphicon-menu-down');
		$('.content').hide(400);
	}
	//$('.content').show(400);
});