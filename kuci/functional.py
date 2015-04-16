import smtplib

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.header import Header
from email import Encoders

from members.models import *
from kuci_settings import *

import coolsms, datetime

def send_gmail(to, subject, text, html):
	msg = MIMEMultipart('alternative')
	msg['From'] = gmail_username
	msg['To'] = to
	msg['Subject'] = Header(subject, 'utf-8')
	msg.attach(MIMEText(text, 'plain', 'utf-8'))
	msg.attach(MIMEText(html, 'html', 'utf-8'))

	mailServer = smtplib.SMTP('smtp.gmail.com', 587)
	mailServer.ehlo()
	mailServer.starttls()
	mailServer.ehlo()
	mailServer.login(gmail_user, gmail_pwd)
	mailServer.sendmail(gmail_user, to, msg.as_string())
	mailServer.close()

def send_sms(to, content):
	cs = coolsms.sms()
	cs.charset('utf8')
	cs.setuser(coolsms_username, coolsms_pwd)
	cs.addsms(to.replace('-', '').encode('utf8'), '0000', content)
	res = 0
	if cs.connect():
		res = cs.send()
	cs.disconnect()
	cs.emptyall()
	return res

def send_security_code_sms(phone_number, code):
	try:
		member = Member.objects.get(phone_number=phone_number)
	except:
		return 0

	recents = MemberSMSSend.objects.filter(member=member, created_datetime__gt=datetime.datetime.now()-datetime.timedelta(minutes=3))
	if len(recents) >= 3:
		return 'too many'
	content = code_check_sms_content(member.number, member.name, phone_number, code)
	res = send_sms(phone_number, content)
	if res:
		tmp = MemberSMSSend.objects.create(member=member)
		tmp.save()
	return res

def send_verify_code_mail(email_verify):
	subject = code_check_email_subject
	content = code_check_email_content(email_verify.email, email_verify.code)
	send_gmail(email_verify.email, subject, '', content)