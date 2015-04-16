# -*- coding: utf-8 -*-

from models import *
from members.models import *

import random

def get_page_nums(total_page_num, pagecount_per_line, page_num):
	if total_page_num < pagecount_per_line:
		pagecount_per_line = total_page_num
		start_p = 1
	else:
		start_p = max(page_num-(pagecount_per_line-1)/2,1)
	if start_p+pagecount_per_line > total_page_num:
		start_p = total_page_num-pagecount_per_line+1
	page_nums = []
	for p in range(start_p, start_p+pagecount_per_line):
		if p <= total_page_num:
			page_nums.append(p)
	return page_nums

def make_random_name(name_set):
	adjectives = u'까칠한-살찐-멋있는-못생긴-잘생긴-바보같은-재미있는-심심한-나태한-재미없는-외로운-화난-귀여운-깜찍한-상큼한'.split('-')
	nouns = u'호랑이-독수리-팬더-강아지-고양이-원숭이-개미핥기-기니피그-돌고래-토끼-쥐-당나귀-돼지-코끼리-악어-다람쥐-두더지-코뿔소'.split('-')

	while True:
		name = ' '.join((random.choice(adjectives), random.choice(nouns)))
		if name not in name_set:
			break
	return name

def get_writer_name(board, article, user):
	if not board.is_anonymous:
		return ''

	if article is None:
		return u'작성자'

	if article.user == user:
		return article.writer_name
	try:
		comment = Comment.objects.filter(article=article, user=user)[0]
		return comment.writer_name
	except:
		name_set = set([comment.writer_name for comment in Comment.objects.filter(article=article)])
		return make_random_name(name_set)

