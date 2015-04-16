
function phone_number_relax(){
	var tmp = $('#inputPhoneNumber').val();
	if (tmp.length == 11){
		var phone_number = tmp.slice(0, 3) + '-' + tmp.slice(3, 7) + '-' + tmp.slice(7, 11);
		$('#inputPhoneNumber').val(phone_number);
	}
}
$('#findID').click(function(){
	phone_number_relax();
	var number = $('#inputNumber').val();
	var name = $('#inputName').val();
	var phone_number = $('#inputPhoneNumber').val();
	$('#myModalLabel').html('아이디 찾기');
	$('#myNumber').html(number);
	$('#myName').html(name);
	$('#myPhoneNumber').html(phone_number);
	$('[role="alert"]').hide();
	$('.hidefindid').hide();
	$('#loading_img').show();
	$.ajax({
		url: '/ajax/members/find_id/',
		type: 'post',
		data: {
			number: number,
			name: name,
			phone_number: phone_number,
			csrfmiddlewaretoken: csrf_token
		},
		success: function(rsp){
			if (rsp.error || !rsp.success){
				var html = '<strong>오류!</strong> ';
				if (rsp.msg == 'cant find'){
					html += '등록된 학사정보를 찾을 수 없습니다.';
				}else if (rsp.msg == 'not registered'){
					html += '가입 정보가 없습니다.';
				}else{
					html += '알 수 없는 에러가 발생했습니다.';
				}
				$('.alert-danger').show();
				$('.alert-danger').html(html);
			}else{
				$('.alert-success').show();
				$('.alert-success').html('<strong>성공!</strong> 찾은 아이디는 <strong>' + rsp.username + '</strong> 입니다.');
			}
			$('#loading_img').hide();
		}
	});
	$('#myModal').modal();
});
$('#findPW').click(function(){
	phone_number_relax();
	var number = $('#inputNumber').val();
	var name = $('#inputName').val();
	var phone_number = $('#inputPhoneNumber').val();
	var username = $('#inputUsername').val();
	var email = $('#inputEmail').val();
	$('#myModalLabel').html('비밀번호 찾기');
	$('#myNumber').html(number);
	$('#myName').html(name);
	$('#myPhoneNumber').html(phone_number);
	$('#myUsername').html(username);
	$('#myEmail').html(email);
	$('.hidefindid').show();
	$('[role="alert"]').hide();
	$('#loading_img').show();
	$.ajax({
		url: '/ajax/members/find_pw/',
		type: 'post',
		data: {
			number: number,
			name: name,
			phone_number: phone_number,
			username: username,
			email: email,
			csrfmiddlewaretoken: csrf_token
		},
		success: function(rsp){
			if (rsp.error || !rsp.success){
				var html = '<strong>오류!</strong> ';
				if (rsp.msg == 'cant find'){
					html += '등록된 학사정보를 찾을 수 없습니다.';
				}else if (rsp.msg == 'not registered'){
					html += '가입 정보가 없습니다.';
				}else if (rsp.msg == 'wrong username'){
					html += '등록된 사용자명과 다릅니다.';
				}else if (rsp.msg == 'wrong email'){
					html += '등록된 이메일과 다릅니다.';
				}else{
					html += '알 수 없는 에러가 발생했습니다.';
				}
				$('.alert-danger').show();
				$('.alert-danger').html(html);
			}else{
				$('.alert-success').show();
				$('.alert-success').html('<strong>성공!</strong> 등록된 이메일 <strong>' + email + '</strong>로 새로운 임시비밀번호를 발송했습니다.');
			}
			$('#loading_img').hide();
		}
	});
	$('#myModal').modal();
});