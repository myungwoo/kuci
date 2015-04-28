# -*- coding: utf-8 -*-

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import *
from django.contrib.auth.decorators import login_required

from models import *

import json

rent_min_date = datetime.date(2015, 3, 2)
rent_max_date = datetime.date(2015, 6, 19)

def JsonResponse(data):
	return HttpResponse(json.dumps(data), content_type='application/json')

def classroom_hour_writable(classroom, date, hour):
	timetable = [(0, 0), (9, 0), (10, 30), (12, 0), (13, 0), (14, 0), (15, 30), (17, 0), (18, 0), (19, 0), (20, 0)]
	if classroom.type == 2:
		h, m = hour, 0
	else:
		h, m = timetable[hour]
	now = datetime.datetime.now()
	start_datetime = datetime.datetime(date.year, date.month, date.day, h, m, 0)
	return start_datetime > now and date <= rent_max_date

@login_required
def rent_main(request):
	classrooms = ClassRoom.objects.all().order_by('order')
	return render_to_response('rent/main.html',
		RequestContext(request, {'classrooms': classrooms,
			'min_date': rent_min_date.strftime('%Y-%m-%d'), 'max_date': rent_max_date.strftime('%Y-%m-%d')}))

@login_required
def rent_ajax_get_content(request):
	if not request.is_ajax() or request.method != 'POST':
		raise PermissionDenied()

	date = datetime.datetime.strptime(request.POST['date'], '%Y/%m/%d').date()
	classroom_id = request.POST['classroom_id']

	if date < rent_min_date or date > rent_max_date:
		raise PermissionDenied()

	try:
		classroom = ClassRoom.objects.get(id=classroom_id)
	except:
		raise PermissionDenied()
	rentinfos = RentInfo.objects.filter(date=date, classroom=classroom)

	by_hour = {}
	for rentinfo in rentinfos:
		by_hour[rentinfo.hour] = rentinfo
	hour_range = range(1, 11) if classroom.type == 1 else range(9, 21)

	rows = []
	for hour in hour_range:
		try:
			rentinfo = by_hour[hour]
		except:
			rentinfo = None
		row = {'hour': hour, 'rentinfo': rentinfo, 'valid': classroom_hour_writable(classroom, date, hour)}
		rows.append(row)

	return render_to_response('rent/content.html', RequestContext(request, {'classroom': classroom, 'rows': rows}))

@login_required
def rent_ajax_get_rentinfo(request):
	if not request.is_ajax() or request.method != 'POST':
		raise PermissionDenied()

	rentinfo_id = request.POST['rentinfo_id']

	try:
		rentinfo = RentInfo.objects.get(id=rentinfo_id)
	except:
		raise PermissionDenied()

	if rentinfo.date < rent_min_date or rentinfo.date > rent_max_date:
		raise PermissionDenied()

	return JsonResponse({'date': rentinfo.date.strftime('%Y/%m/%d'), 'hour': rentinfo.hour, 'name': rentinfo.user.first_name, 'reason': rentinfo.reason, 'classroom': str(rentinfo.classroom), 'classroom_type': rentinfo.classroom.type})

@login_required
def rent_ajax_delete_rentinfo(request):
	if not request.is_ajax() or request.method != 'POST':
		raise PermissionDenied()

	rentinfo_id = request.POST['rentinfo_id']

	try:
		rentinfo = RentInfo.objects.get(id=rentinfo_id)
	except:
		raise PermissionDenied()

	if rentinfo.user != request.user and not request.user.is_staff:
		raise PermissionDenied()

	if not classroom_hour_writable(rentinfo.classroom, rentinfo.date, rentinfo.hour) and not request.user.is_staff:
		raise PermissionDenied()

	if rentinfo.date < rent_min_date or rentinfo.date > rent_max_date:
		raise PermissionDenied()

	rentinfo.delete()
	return HttpResponse('yes')

@login_required
def rent_ajax_write_rentinfo(request):
	if not request.is_ajax() or request.method != 'POST':
		raise PermissionDenied()

	rentinfo_id = int(request.POST['rentinfo_id'])
	date = datetime.datetime.strptime(request.POST['date'], '%Y/%m/%d').date()
	classroom_id = int(request.POST['classroom_id'])
	hour = int(request.POST['hour'])
	reason = request.POST['reason']

	try:
		classroom = ClassRoom.objects.get(id=classroom_id)
	except:
		raise PermissionDenied()

	if not classroom_hour_writable(classroom, date, hour) and not request.user.is_staff:
		raise PermissionDenied()

	if date < rent_min_date or date > rent_max_date:
		raise PermissionDenied()

	if rentinfo_id:
		try:
			rentinfo = RentInfo.objects.get(id=rentinfo_id)
		except:
			raise PermissionDenied()

		if (classroom_id, date, hour) != (rentinfo.classroom.id, rentinfo.date, rentinfo.hour):
			raise PermissionDenied()

		if rentinfo.user != request.user and not request.user.is_staff:
			raise PermissionDenied()

		rentinfo.reason = reason
		rentinfo.save()
	else:
		cnt = RentInfo.objects.filter(classroom=classroom, date=date, hour=hour).count()
		if cnt:
			raise PermissionDenied()
		rentinfo = RentInfo.objects.create(classroom=classroom, date=date, hour=hour, reason=reason, user=request.user)
		rentinfo.save()

	return HttpResponse('yes')
