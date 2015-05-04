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

import string, random, datetime, json, re

def JsonResponse(data):
	return HttpResponse(json.dumps(data), content_type='application/json')

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

def members_find_id_pw(request):
	return render_to_response('find_id_pw.html', RequestContext(request, {}))

def members_ajax_find_id(request):
	if not request.is_ajax() or request.method != 'POST':
		raise PermissionDenied()
	number = request.POST['number']
	name = request.POST['name']
	phone_number = request.POST['phone_number']

	try:
		member = Member.objects.get(number=number, name=name, phone_number=phone_number)
	except:
		return JsonResponse({'error': True, 'msg': 'cant find'})

	if not member.user:
		return JsonResponse({'error': True, 'msg': 'not registered'})

	return JsonResponse({'error': False, 'success': True, 'username': member.user.username})

def members_ajax_find_pw(request):
	if not request.is_ajax() or request.method != 'POST':
		raise PermissionDenied()

	number = request.POST['number']
	name = request.POST['name']
	phone_number = request.POST['phone_number']
	username = request.POST['username']
	email = request.POST['email']

	try:
		member = Member.objects.get(number=number, name=name, phone_number=phone_number)
	except:
		return JsonResponse({'error': True, 'msg': 'cant find'})

	if not member.user:
		return JsonResponse({'error': True, 'msg': 'not registered'})

	user = member.user
	if user.username != username:
		return JsonResponse({'error': True, 'msg': 'wrong username'})
	if user.email != email:
		return JsonResponse({'error': True, 'msg': 'wrong email'})

	new_password = ''.join([random.choice(string.ascii_letters) for i in xrange(8)])
	user.set_password(new_password)
	user.save()
	send_new_password_mail(user, new_password)
	return JsonResponse({'error': False, 'success': True})

def members_privacy(request):
	return render_to_response('privacy.html', RequestContext(request, {}))

def check_member_list(member_list, err_list, members):
	for arr in member_list:
		if not ''.join(arr):
			continue
		if len(arr) != 3:
			err_list.append(u'형식에 맞지 않는 줄: %s'%('\t'.join(arr)))
			continue
		number, name, phone_number = arr
		try:
			member = Member.objects.get(number=number)
		except:
			member = None
		if member and member.name != name:
			err_list.append(u'이전에 입력된 이름과 다름: (기존 이름: %s, 현재 이름: %s)'%(member.name, name))
			continue
		if re.match('^\+82 10-\d{4}-\d{4}$', phone_number):
			phone_number = '010-%s-%s'%(phone_number[7:11], phone_number[12:16])
		if re.match('^010\d{8}$', phone_number):
			phone_number = '010-%s-%s'%(phone_number[3:7], phone_number[7:11])
		if not re.match('^010-\d{4}-\d{4}', phone_number):
			err_list.append(u'올바르지 않은 연락처 형식: %s'%phone_number)
			continue
		members.append([number, name, phone_number])

@login_required
def members_update(request):
	user = request.user
	if not user.is_staff:
		raise PermissionDenied()
	if request.method == 'POST':
		member_list1 = map(lambda x: x.strip().split('\t'), request.POST['member_list1'].split('\n'))
		member_list2 = map(lambda x: x.strip().split('\t'), request.POST['member_list2'].split('\n'))

		err_list1 = []
		members1 = []
		err_list2 = []
		members2 = []
		check_member_list(member_list1, err_list1, members1)
		check_member_list(member_list2, err_list2, members2)

		if err_list1 or err_list2:
			return render_to_response('update.html', RequestContext(request, {'err_list1': err_list1, 'err_list2': err_list2, 'member_list1': request.POST['member_list1'], 'member_list2': request.POST['member_list2']}))

		for member in Member.objects.filter(type__in=[1, 2]):
			member.type = 3
			member.save()

		member_list1 = []
		for number, name, phone_number in members1:
			try:
				member = Member.objects.get(number=number)
				if member.phone_number != phone_number:
					member.phone_number = phone_number
				if member.type != 1:
					member.type = 1
			except:
				member = Member.objects.create(type=1, number=number, name=name, phone_number=phone_number)
			member.save()
			member_list1.append(member)

		member_list2 = []
		for number, name, phone_number in members2:
			try:
				member = Member.objects.get(number=number)
				if member.phone_number != phone_number:
					member.phone_number = phone_number
				if member.type != 2:
					member.type = 2
			except:
				member = Member.objects.create(type=2, number=number, name=name, phone_number=phone_number)
			member.save()
			member_list2.append(member)
		return render_to_response('update_result.html', RequestContext(request, {'members1': member_list1, 'members2': member_list2}))

	return render_to_response('update.html', RequestContext(request, {}))
