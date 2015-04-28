# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

import datetime

class ClassRoom(models.Model):
	ROOM_TYPE = (\
		(1, '일반 강의실'),\
		(2, '세미나실'),\
	)
	type = models.IntegerField(choices=ROOM_TYPE, default=1)
	display_name = models.CharField(max_length=20)
	room_size = models.IntegerField(default=0)
	order = models.IntegerField(default=0)

	def __unicode__(self):
		return u'''%s%s / %d석''' % (unicode(self.display_name), u'(세미나실)' if self.type == 2 else '', self.room_size)

class RentInfo(models.Model):
	classroom = models.ForeignKey(ClassRoom)
	user = models.ForeignKey(User)
	date = models.DateField(default=datetime.date.today())
	reason = models.CharField(max_length=200)
	hour = models.IntegerField(default=1)

	def __unicode__(self):
		return u'''%s rent classroom %s at %s''' % (unicode(self.user.first_name), unicode(self.classroom.display_name), unicode(self.hour))