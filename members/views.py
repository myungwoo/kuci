# -*- coding: utf-8 -*-

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import *
from django.contrib.auth.decorators import login_required

from django.core.exceptions import PermissionDenied

from models import *
from kuci.kuci_settings import *
from kuci.functional import *

from django.views.decorators.csrf import csrf_exempt

import string, random, datetime

def members_make_security(request):
	if not request.is_ajax() or request.method != 'POST':
		raise PermissionDenied()
	number = request.POST['number']
	name = request.POST['name']
	phone_number = request.POST['phone_number']
	try:
		member = Member.objects.get(number=number, name=name, phone_number=phone_number)
	except:
		return HttpResponse('unknown')
	if member.user:
		return HttpResponse('exist')
	candidate = string.digits
	code = ''.join([random.choice(candidate) for i in xrange(6)])
	member.security_code = code
	member.save()
	res = send_security_code_sms(phone_number=phone_number, code=code)
	if res == 'too many':
		return HttpResponse('too many')
	if not res:
		return HttpResponse('error')
	return HttpResponse('yes')

def members_code_check(request):
	if not request.is_ajax() or request.method != 'POST':
		raise PermissionDenied()
	number = request.POST['number']
	name = request.POST['name']
	phone_number = request.POST['phone_number']
	code = request.POST['code']
	try:
		member = Member.objects.get(number=number, name=name, phone_number=phone_number)
	except:
		return HttpResponse('unknown')
	if member.security_code == code:
		return HttpResponse('yes')
	return HttpResponse('wrong')

def members_username_duplication_check(request):
	if not request.is_ajax() or request.method != 'POST':
		raise PermissionDenied()
	username = request.POST['username']
	try:
		user = User.objects.get(username=username)
	except:
		return HttpResponse('no')
	return HttpResponse('exists')

def members_send_verify_email(request):
	if not request.is_ajax() or request.method != 'POST':
		raise PermissionDenied()
	email = request.POST['email']
	email_verify, _ = EmailVerification.objects.get_or_create(email=email)
	if email_verify.joined:
		return HttpResponse('joined')
	code = ''.join([random.choice(string.ascii_letters) for i in xrange(10)])
	email_verify.code = code
	email_verify.save()
	send_verify_code_mail(email_verify)
	return HttpResponse('yes')

def members_check_verify_code(request):
	if not request.is_ajax() or request.method != 'POST':
		raise PermissionDenied()
	email = request.POST['email']
	code = request.POST['code']
	try:
		email_verify = EmailVerification.objects.get(email=email, code=code)
	except:
		return HttpResponse('no')
	email_verify.verified = True
	email_verify.save()
	return HttpResponse('yes')

def members_register(request):
	if request.method == 'GET':
		return render_to_response('register.html', RequestContext(request, {}))
	number = request.POST['number']
	name = request.POST['name']
	phone_number = request.POST['phone_number']
	code = request.POST['code']
	email = request.POST['email']
	username = request.POST['username']
	password = request.POST['password1']
	get_email = request.POST.get('get_email', 'off')
	try:
		member = Member.objects.get(number=number, name=name, phone_number=phone_number)
	except:
		raise PermissionDenied()
	if member.security_code != code:
		raise PermissionDenied()
	if member.user:
		return HttpResponseRedirect('/')
	try:
		email_verify = EmailVerification.objects.get(email=email)
	except:
		raise PermissionDenied()
	if not email_verify.verified or email_verify.joined:
		raise PermissionDenied()
	email_verify.joined = True
	first_name = member.number[2:4] + member.name
	user = User.objects.create_user(username=username, password=password, email=email, last_name='', first_name=first_name)
	member.get_email = (get_email != 'off')
	member.user = user
	member.save()
	return render_to_response('register_complete.html', RequestContext(request, {'member': member, 'email': email}))

@login_required
def members_change_info(request):
	try:
		member = Member.objects.get(user=request.user)
	except:
		member = None
	if request.method == 'GET':
		return render_to_response('change_info.html', RequestContext(request, {'member': member}))
	user = request.user
	cur_password = request.POST['cur_password']
	password = request.POST['password1']
	if not request.user.check_password(cur_password):
		return render_to_response('change_info.html', RequestContext(request, {'member': member, 'password_error': True}))
	get_email = request.POST.get('get_email', 'off')
	email = request.POST.get('email', '')
	if email:
		try:
			email_verify_new = EmailVerification.objects.get(email=email)
		except:
			raise PermissionDenied()
		try:
			email_verify_old = EmailVerification.objects.get(email=user.email)
		except:
			email_verify_old = None
		if not email_verify_new.verified or email_verify_new.joined:
			raise PermissionDenied()
		user.email = email
		user.save()
		email_verify_new.joined = True
		email_verify_new.save()
		if email_verify_old:
			email_verify_old.delete()

	if member:
		member.get_email = (get_email != 'off')
		member.save()
	if password:
		user.set_password(password)
	user.save()
	return HttpResponseRedirect('/')

def members_privacy(request):
	return render_to_response('privacy.html', RequestContext(request, {}))
