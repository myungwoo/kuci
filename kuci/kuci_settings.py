# -*- coding: utf-8 -*-

gmail_username = u'고려대학교 정보대학 학생회'
gmail_user = 'kuci.bon@gmail.com'
gmail_pwd = '' # gmail password

coolsms_username = 'kuci'
coolsms_pwd = '' # coolsms password

def code_check_sms_content(number, name, phone_number, code):
	return '''[고려대학교 정보대학 학생회]
%s님의 본인 인증 코드: %s'''%(name.encode('utf8'), code.encode('utf8'))

code_check_email_subject = u'고려대학교 정보대학 학생회 홈페이지 인증 확인 메일'

def code_check_email_content(email, code):
	return u'''안녕하세요.<br/>
고려대학교 정보대학 제1대 학생회 本 입니다.<br/>
회원 가입을 위해 메일 인증을 해야합니다.<br/>
메일 인증 코드는 아래와 같습니다.<br/>
<br/>
%s<br/>
<br/>
가입해주셔서 감사합니다.</br>
민족고대 첨단정보 제1대 학생회 本 드림'''%(code)

new_password_email_subject = u'고려대학교 정보대학 학생회 홈페이지 비밀번호 찾기'

def new_password_email_content(user, new_password):
	return u'''안녕하세요.<br/>
고려대학교 정보대학 제1대 학생회 本 입니다.<br/>
비밀번호 찾기 요청이 들어와서 새로 비밀번호를 설정하였습니다.<br/>
새로 설정된 비밀번호는 아래와 같습니다.<br/>
<br/>
%s<br/>
<br/>
감사합니다</br>
민족고대 첨단정보 제1대 학생회 本 드림'''%(new_password)