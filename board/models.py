# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User, Group

import datetime

class FileUpload(models.Model):
	upload = models.FileField(upload_to="uploads/%Y/%m/%d/")
	user = models.ForeignKey(User)
	created_datetime = models.DateTimeField(auto_now_add=True)
	is_image = models.BooleanField(default=True)

	def __unicode__(self):
		size = self.upload.size
		size_str = '%d KB'%(size/1024) if size < 1024*1024 else '%.2f MB'%(float(size)/1024/1024)
		return u'''[%s] %s (%s)''' % (u'이미지' if self.is_image else u'파일', unicode(self.upload), size_str)

class Board(models.Model):
	name = models.CharField(max_length=15, unique=True)
	view_name = models.CharField(max_length=30)
	description = models.CharField(max_length=80)
	article_per_page = models.IntegerField(default=20)
	staff_only = models.BooleanField(default=False)
	is_anonymous = models.BooleanField(default=False)
	is_new_hours = models.IntegerField(default=24*3)
	is_hot_minutes = models.IntegerField(default=60)
	is_hot_counts = models.IntegerField(default=10)
	created_datetime = models.DateTimeField(auto_now_add=True)

	@property
	def article_count(self):
		return Article.objects.filter(board=self, deleted=False).count()

	def __unicode__(self):
		return u'''[%s] %s'''%(self.name, self.view_name)

class Article(models.Model):
	board = models.ForeignKey(Board)
	num = models.IntegerField(default=0)
	user = models.ForeignKey(User)
	writer_name = models.CharField(max_length=20, null=True, blank=True)
	title = models.CharField(max_length=30)
	content = models.TextField()
	is_important = models.BooleanField(default=False)
	deleted = models.BooleanField(default=False)
	created_datetime = models.DateTimeField(auto_now_add=True)

	@property
	def is_new(self):
		return (datetime.datetime.now()-self.created_datetime) < datetime.timedelta(hours=self.board.is_new_hours)

	@property
	def is_hot(self):
		return Comment.objects.filter(article=self, created_datetime__gt=(datetime.datetime.now()-datetime.timedelta(minutes=self.board.is_hot_minutes))).count() >= self.board.is_hot_counts

	@property
	def read_count(self):
		return ReadInfo.objects.filter(article=self).count()

	@property
	def display_date(self):
		return self.created_datetime.strftime('%Y-%m-%d')

	@property
	def display_datetime(self):
		return self.created_datetime.strftime('%Y-%m-%d %H:%M:%S')

	@property
	def comment_count(self):
		return Comment.objects.filter(article=self, deleted=False).count()

	def __unicode__(self):
		return u'''[%s] %s'''%(self.user.username, self.title)

class Comment(models.Model):
	article = models.ForeignKey(Article)
	user = models.ForeignKey(User)
	writer_name = models.CharField(max_length=20)
	content = models.TextField()
	deleted = models.BooleanField(default=False)
	created_datetime = models.DateTimeField(auto_now_add=True)

	@property
	def display_datetime(self):
		return self.created_datetime.strftime('%Y-%m-%d %H:%M:%S')

	def __unicode__(self):
		return u'''[%s] %s'''%(self.user.username, self.article.title)

class ReadInfo(models.Model):
	article = models.ForeignKey(Article)
	user = models.ForeignKey(User)
	created_datetime = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return u'''[%s] %s'''%(self.user.username, self.article.title)


