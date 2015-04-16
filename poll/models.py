# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User, Group

from members.models import *

import datetime

class Poll(models.Model):
	name = models.CharField(max_length=40, unique=True)
	view_name = models.CharField(max_length=50)
	need_authentication = models.BooleanField(default=False) # 문자 인증 기능을 사용할 것인지
	do_offline_vote = models.BooleanField(default=False) # 오프라인 투표도 진행할 것인지
	regular_only = models.BooleanField(default=True) # 정회원만 투표 가능한지
	only_choice = models.BooleanField(default=True) # 단일 선택인지
	maximum_choice_count = models.IntegerField(default=0) # 최대 선택 개수(복수 선택일 경우만, 0이면 제한 없음)
	hide_voter = models.BooleanField(default=False) # 비밀 투표인지
	result_hide = models.BooleanField(default=True) # 결과 페이지를 숨길 것인지
	start_time = models.DateTimeField(default=datetime.datetime.now())
	end_time = models.DateTimeField(default=datetime.datetime.now()+datetime.timedelta(days=2))
	deleted = models.BooleanField(default=False)
	created_datetime = models.DateTimeField(auto_now_add=True)

	@property
	def display_start_time(self):
		return self.start_time.strftime('%Y-%m-%d %H:%M:%S')

	@property
	def display_end_time(self):
		return self.end_time.strftime('%Y-%m-%d %H:%M:%S')

	@property
	def voted_count(self):
		return MemberVoteInfo.objects.filter(poll=self).count()

	@property
	def online_voted_count(self):
		return MemberVoteInfo.objects.filter(poll=self, is_offline=False).count()

	@property
	def offline_voted_count(self):
		return MemberVoteInfo.objects.filter(poll=self, is_offline=True).count()

	@property
	def voter_count(self):
		ret = Member.objects.filter(type=1).count()
		if not self.regular_only:
			ret += Member.objects.filter(type=2).count()
		return ret

	@property
	def voted_rate(self):
		a = self.voted_count
		b = self.voter_count
		if b == 0:
			return '- %'
		rate = float(a)/b*100
		return '%.2f %%'%rate

	@property
	def status(self):
		now = datetime.datetime.now()
		if now < self.start_time:
			return 'wait'
		elif now > self.end_time:
			return 'end'
		return 'during'

	def __unicode__(self):
		return u'''[%s] %s'''%(self.name, self.view_name)

class Choice(models.Model):
	poll = models.ForeignKey(Poll)
	title = models.CharField(max_length=20)
	created_datetime = models.DateTimeField(auto_now_add=True)

	@property
	def percentage(self):
		a = UserChoiceInfo.objects.filter(poll=self.poll, choice=self).count()
		b = self.poll.online_voted_count
		p = float(a)/b*100 if b else 0
		return '%.0f'%p

	def __unicode__(self):
		return u'''[%s] %s'''%(self.poll.view_name, self.title)

class UserChoiceInfo(models.Model):
	user = models.ForeignKey(User, null=True, blank=True)
	poll = models.ForeignKey(Poll)
	choice = models.ForeignKey(Choice)
	created_datetime = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return u'''%s voted at %s (%s)'''%(self.user.username if self.user else 'Unknown', self.poll.view_name, self.choice.title)

class MemberVoteInfo(models.Model):
	member = models.ForeignKey(Member)
	poll = models.ForeignKey(Poll)
	is_offline = models.BooleanField(default=False)
	created_datetime = models.DateTimeField(auto_now_add=True)

	@property
	def display_datetime(self):
		return self.created_datetime.strftime('%Y-%m-%d %H:%M:%S')

	def __unicode__(self):
		return u'''%s voted at %s'''%(self.member.name, self.poll.view_name)