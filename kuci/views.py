from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import *
from django.views.static import serve

import os

@login_required
def views_calendar(request):
	return render_to_response('calendar.html', RequestContext(request, {}))

def views_static_serve(request, path):
 	return serve(request, path, os.path.join(os.path.dirname(__file__),'../static/'), False)

def views_403(request):
	path = request.path
	return render_to_response('403.html', RequestContext(request, {'path': path}))

def views_404(request):
	path = request.path
	return render_to_response('404.html', RequestContext(request, {'path': path}))

def views_500(request):
	return render_to_response('500.html', RequestContext(request, {}))