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

# Create your views here.
def rent_main(request):
	return render_to_response('rent/main.html', RequestContext(request, {}))