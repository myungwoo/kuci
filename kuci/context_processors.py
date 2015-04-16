
from poll.models import *
from poll.permissions import *

import datetime

def default(request):

	if request.user:
		user = request.user
		now = datetime.datetime.now()
		polls = Poll.objects.filter(deleted=False, start_time__lte=now, end_time__gte=now)
		not_voted_count = len([poll for poll in polls if get_users_poll_status(poll, user) == 1])
	else:
		not_voted_count = 0
	return dict(
		example = "This is an example string.", # don't forget the commas!
		not_voted_count = not_voted_count,
	)