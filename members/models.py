# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User, Group

class Member(models.Model):
	MEMBER_TYPE = (\
		(1, '정회원'),\
		(2, '준회원'),\
		(3, '졸업생 혹은 자퇴생'),\
		(4, '교직원'),\
	)
	type = models.IntegerField(choices=MEMBER_TYPE, default=2)
	number = models.CharField(max_length=10, unique=True)
	name = models.CharField(max_length=30)
	phone_number = models.CharField(max_length=13)
	user = models.ForeignKey(User, null=True, blank=True, unique=True)
	security_code = models.CharField(max_length=8, null=True, blank=True)
	get_email = models.BooleanField(default=False)

	def __unicode__(self):
		return u'''[%s] %s''' % (unicode(self.get_type_display()), unicode(self.name))

class MemberSMSSend(models.Model):
	member = models.ForeignKey(Member)
	created_datetime = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return u'''Send SMS to %s at %s'''%(self.member.name, self.created_datetime.strftime('%Y-%m-%d %H:%M:%S'))

class EmailVerification(models.Model):
	email = models.CharField(max_length=40, unique=True)
	code = models.CharField(max_length=30, blank=True, null=True)
	verified = models.BooleanField(default=False)
	joined = models.BooleanField(default=False)

	def __unicode__(self):
		return u'''[%s] %s'''%('Verified' if self.verified else 'Not verified', self.email)