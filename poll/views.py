# -*- coding: utf-8 -*-

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied

from django.views.static import serve
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from models import *
from members.models import *
from permissions import *
from kuci.functional import *

import os, json, string, random

def JsonResponse(data):
	return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
def poll_make_security(request, poll_name=None):
	if not request.is_ajax() or request.method != 'POST':
		raise PermissionDenied()
	if poll_name is None:
		raise PermissionDenied()
	try:
		poll = Poll.objects.get(name=poll_name)
	except:
		raise Http404()
	user = request.user
	user_status = get_users_poll_status(poll, user)
	if user_status != 1:
		raise PermissionDenied()
	try:
		member = Member.objects.get(user=user)
	except:
		return HttpResponse('error')
	candidate = string.digits
	code = ''.join([random.choice(candidate) for i in xrange(6)])
	member.security_code = code
	member.save()
	res = send_security_code_sms(phone_number=member.phone_number, code=code)
	if res == 'too many':
		return HttpResponse('too many')
	if not res:
		return HttpResponse('error')
	return HttpResponse('yes')

@login_required
def poll_code_check(request, poll_name=None):
	if not request.is_ajax() or request.method != 'POST':
		raise PermissionDenied()
	if poll_name is None:
		raise PermissionDenied()
	try:
		poll = Poll.objects.get(name=poll_name)
	except:
		raise Http404()
	user = request.user
	code = request.POST['code']
	try:
		member = Member.objects.get(user=user)
	except:
		return HttpResponse('unknown')
	if member.security_code == code:
		return HttpResponse('yes')
	return HttpResponse('wrong')

@login_required
def poll_list(request):
	polls = Poll.objects.filter(deleted=False).order_by('-id')
	available_polls = [poll for poll in polls if user_vote_permission(poll, request.user)]
	voted_polls = [poll for poll in available_polls if is_user_voted(poll, request.user)]

	return render_to_response('poll/list.html', RequestContext(request, {'polls': polls, 'available_polls': available_polls, 'voted_polls': voted_polls}))

@login_required
def poll_view(request, poll_name=None):
	if poll_name is None:
		raise PermissionDenied()
	try:
		poll = Poll.objects.get(name=poll_name)
	except:
		raise Http404()

	user = request.user
	user_status = get_users_poll_status(poll, user)
	try:
		member = Member.objects.get(user=user)
	except:
		member = None
	if request.method == 'GET':
		choices = Choice.objects.filter(poll=poll).order_by('id')
		return render_to_response('poll/view.html', RequestContext(request, {'poll': poll, 'choices': choices, 'user_status': user_status, 'member': member}))

	if user_status != 1 or poll.status != 'during' or not member:
		raise PermissionDenied()
	if poll.need_authentication:
		code = request.POST.get('code', '')
		if not member or member.security_code != code:
			raise PermissionDenied()
	if poll.only_choice:
		value = request.POST.get('choice', None)
		values = [value]
	else:
		values = request.POST.getlist('choice')
		if poll.maximum_choice_count and len(values) > poll.maximum_choice_count or not values:
			raise PermissionDenied()
	try:
		choices = map(lambda x: Choice.objects.get(id=x, poll=poll), values)
	except:
		raise PermissionDenied()
	mvi = MemberVoteInfo.objects.create(member=member, poll=poll, is_offline=False)
	mvi.save()
	for choice in choices:
		uci = UserChoiceInfo.objects.create(user=None if poll.hide_voter else user, poll=poll, choice=choice)
		uci.save()

	return HttpResponseRedirect('/poll/'+poll.name+'/')

@login_required
def poll_result(request, poll_name=None):
	if poll_name is None:
		raise PermissionDenied()
	try:
		poll = Poll.objects.get(name=poll_name)
	except:
		raise Http404()

	user = request.user
	if not user.is_superuser and poll.result_hide:
		raise PermissionDenied()

	choices = Choice.objects.filter(poll=poll).order_by('id')

	return render_to_response('poll/result.html', RequestContext(request, {'poll': poll, 'choices': choices}))

@login_required
def poll_offline(request, poll_name=None):
	if poll_name is None:
		raise PermissionDenied()
	try:
		poll = Poll.objects.get(name=poll_name)
	except:
		raise Http404()

	user = request.user
	if not user.is_staff or not poll.do_offline_vote:
		raise PermissionDenied()

	if request.method == 'GET':
		return render_to_response('poll/offline.html', RequestContext(request, {'poll': poll}))
	
	number = request.POST['number']
	name = request.POST['name']
	try:
		member = Member.objects.get(number=number, name=name)
	except:
		raise PermissionDenied()
	if is_member_voted(poll, member) or not member_vote_permission(poll, member):
		raise PermissionDenied()
	mvi = MemberVoteInfo.objects.create(poll=poll, member=member, is_offline=True)
	mvi.save()
	return render_to_response('poll/offline_complete.html', RequestContext(request, {'poll': poll, 'member': member}))

@login_required
def poll_check_voted(request, poll_name=None):
	if not request.is_ajax():
		raise PermissionDenied()
	if poll_name is None:
		raise PermissionDenied()
	try:
		poll = Poll.objects.get(name=poll_name)
	except:
		raise Http404()

	user = request.user
	if not user.is_staff or not poll.do_offline_vote:
		return HttpResponseNotFound()
	number = request.POST['number']
	name = request.POST['name']
	try:
		member = Member.objects.get(number=number, name=name)
	except:
		return HttpResponse('no member info')
	if not member_vote_permission(poll=poll, member=member):
		return HttpResponse('no permission')
	try:
		mvi = MemberVoteInfo.objects.get(member=member, poll=poll)
	except:
		return HttpResponse('not voted')
	if mvi.is_offline:
		return HttpResponse('offline')
	return HttpResponse('online')

@login_required
def poll_voter_list(request, poll_name=None):
	if poll_name is None:
		raise PermissionDenied()
	try:
		poll = Poll.objects.get(name=poll_name)
	except:
		raise Http404()

	user = request.user
	if not user.is_staff:
		raise PermissionDenied()

	voters = MemberVoteInfo.objects.filter(poll=poll).order_by('id')
	return render_to_response('poll/voter_list.html', RequestContext(request, {'poll': poll, 'voters': voters}))

@login_required
def poll_delete_offline_voter(request, poll_name=None, info_id=0):
	if poll_name is None:
		raise PermissionDenied()
	try:
		poll = Poll.objects.get(name=poll_name)
	except:
		raise Http404()

	user = request.user
	if not user.is_staff or poll.status != 'during':
		raise PermissionDenied()

	try:
		voter = MemberVoteInfo.objects.get(id=info_id)
	except:
		raise Http404()

	if not voter.is_offline:
		raise PermissionDenied()
	voter.delete()
	return HttpResponseRedirect('/poll/' + poll.name + '/voter_list/')

@login_required
def poll_get_voters(request):
	if not request.is_ajax() or request.method != 'POST':
		raise PermissionDenied()

	choice_id = request.POST['choice_id']
	choice = Choice.objects.get(id=choice_id)
	poll = choice.poll
	if poll.hide_voter or poll.result_hide:
		raise PermissionDenied()
	infos = UserChoiceInfo.objects.filter(choice__id=choice_id).order_by('-id')
	voters = map(lambda x: x.user.first_name, infos)
	return JsonResponse({'choice_title': choice.title, 'voters': voters})


