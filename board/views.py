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

from django.db.models import Max, Q

from models import *
from functional import *

import os, operator, json, hashlib, re

def JsonResponse(data):
	return HttpResponse(json.dumps(data), content_type='application/json')

def get_safe(html):
	return re.sub(re.compile('</?script.*?>'), '', html)

def board_upload_serve(request, path):
 	return serve(request, path, os.path.join(os.path.dirname(__file__),'../database/uploads/'), False)

@csrf_exempt
@login_required
def board_upload_image(request):
	if not request.is_ajax() or request.method != 'POST':
		raise PermissionDenied()
	images = {}
	for f in request.FILES.getlist('file'):
		if f.size > 500*1024:
			return JsonResponse({'error_msg': u'최대 용량 제한: 500KB', 'error': True})
		name, ext = os.path.splitext(f.name)
		m = hashlib.md5()
		m.update(name.encode('utf-8'))
		f.name = '%s%s'%(m.hexdigest(), ext)
		obj = FileUpload.objects.create(upload=f, is_image=True, user=request.user)
		images = {'filelink': obj.upload.url}
	return JsonResponse(images)

@csrf_exempt
@login_required
def board_upload_file(request):
	if not request.is_ajax() or request.method != 'POST':
		raise PermissionDenied()
	if not request.user.is_staff:
		return JsonResponse({'error_msg': u'스태프만 파일 업로드 가능합니다.', 'error': True})
	files = {}
	for f in request.FILES.getlist('file'):
		if f.size > 5*1024*1024:
			return JsonResponse({'error_msg': u'최대 용량 제한: 5MB', 'error': True})
		name, ext = os.path.splitext(f.name)
		m = hashlib.md5()
		m.update(name.encode('utf-8'))
		f.name = '%s%s'%(m.hexdigest(), ext)
		obj = FileUpload.objects.create(upload=f, is_image=False, user=request.user)
		files = {'filelink': obj.upload.url, 'filename': u'%s%s'%(name, ext)}
	return JsonResponse(files)

@login_required
def board_article_list(request, board_name=None, page_num=1):
	if board_name is None:
		raise PermissionDenied()
	try:
		board = Board.objects.get(name=board_name)
	except:
		raise Http404()

	search_type = request.GET.get('search_type', '')
	query = request.GET.get('query', '')
	is_search = True
	if search_type == 'title':
		articles = Article.objects.filter(board=board, deleted=False, is_important=False, title__contains=query).order_by('-id')
	elif search_type == 'content':
		articles = Article.objects.filter(board=board, deleted=False, is_important=False, content__contains=query).order_by('-id')
	elif search_type == 'title.content':
		q = operator.and_(operator.or_(Q(title__contains=query), Q(content__contains=query)), Q(board=board, deleted=False, is_important=False))
		articles = Article.objects.filter(q).order_by('-id')
	elif search_type == 'username' and not board.is_anonymous:
		articles = Article.objects.filter(board=board, deleted=False, is_important=False, user__username=query).order_by('-id')
	elif search_type == 'name' and not board.is_anonymous:
		articles = Article.objects.filter(board=board, deleted=False, is_important=False, writer_name__contains=query).order_by('-id')
	else:
		articles = Article.objects.filter(board=board, deleted=False, is_important=False).order_by('-id')
		is_search = False

	count_per_page = board.article_per_page
 	total_page_num = max((articles.count()-1)/count_per_page+1,1)
 	page_num = int(page_num)
 	if page_num < 1 or page_num > total_page_num:
 		raise Http404()
 	start = (page_num-1)*count_per_page; end = page_num*count_per_page
 	articles = articles[start:end]

 	page_nums = get_page_nums(total_page_num, 5, page_num)

 	important_articles = Article.objects.filter(board=board, deleted=False, is_important=True).order_by('-id')
	article_count = articles.count() + important_articles.count()

 	return render_to_response('board/article_list.html', RequestContext(request,
 		{'board': board, 'articles': articles, 'page_num': page_num, 'total_page_num': total_page_num,
 		'page_nums': page_nums, 'get_parameters': request.GET.urlencode(), 'get_dict': request.GET,
 		'article_count': article_count, 'is_search': is_search, 'important_articles': important_articles}))

@login_required
def board_article_view(request, board_name=None, article_num=0):
	if board_name is None:
		raise PermissionDenied()
	try:
		board = Board.objects.get(name=board_name)
		article = Article.objects.get(board=board, num=article_num)
	except:
		raise Http404()

	if not request.user.is_staff and article.deleted:
		raise Http404()

	user = request.user
	readinfo = ReadInfo.objects.get_or_create(user=user, article=article)
	comments = Comment.objects.filter(article=article, deleted=False).order_by('id')

	try:
		next_article = Article.objects.filter(board=board, deleted=False, id__gt=article_id).order_by('id')[0]
	except:
		next_article = None
	try:
		prev_article = Article.objects.filter(board=board, deleted=False, id__lt=article_id).order_by('-id')[0]
	except:
		prev_article = None

	return render_to_response('board/article_view.html', RequestContext(request,
 		{'board': board, 'article': article, 'comments': comments, 'next_article': next_article, 'prev_article': prev_article}))

@login_required
def board_article_delete(request, board_name=None, article_num=0):
	if board_name is None:
		raise PermissionDenied()
	try:
		board = Board.objects.get(name=board_name)
		article = Article.objects.get(board=board, num=article_num)
	except:
		raise Http404()

	if article.board != board:
		raise Http404()

	if article.user != request.user and not request.user.is_staff:
		raise PermissionDenied()

	board = article.board
	article.deleted = True
	article.save()

	return HttpResponseRedirect('/board/%s/'%(board.name))

@login_required
def board_article_write(request, board_name=None):
	if board_name is None:
		raise PermissionDenied()
	try:
		board = Board.objects.get(name=board_name)
	except:
		raise Http404()

	if board.staff_only and not request.user.is_staff:
		raise PermissionDenied()

	if request.method == 'GET':
		return render_to_response('board/article_write.html', RequestContext(request, {'board': board}));

	num = Article.objects.filter(board=board).aggregate(Max('num'))['num__max']+1 if Article.objects.filter(board=board).count() else 1
	title = request.POST.get('title', '')
	content = get_safe(request.POST.get('content', ''))
	writer_name = get_writer_name(board, None, request.user)
	is_important = request.POST.get('is_important', False) and request.user.is_staff

	article = Article.objects.create(num=num, user=request.user, board=board, title=title, content=content, is_important=is_important, writer_name=writer_name)
	return HttpResponseRedirect('/board/%s/view/%d/'%(board.name, article.num))

@login_required
def board_comment_delete(request, board_name=None, comment_id=0):
	if board_name is None:
		raise PermissionDenied()
	try:
		comment = Comment.objects.get(id=comment_id)
		board = Board.objects.get(name=board_name)
	except:
		raise Http404()
	
	if comment.user != request.user and not request.user.is_staff:
		raise PermissionDenied()

	if comment.article.board != board:
		raise Http404()

	article = comment.article
	comment.deleted = True
	comment.save()

	return HttpResponseRedirect('/board/%s/view/%d/'%(article.board.name, article.num))

@require_POST
@login_required
def board_comment_write(request, board_name=None, article_num=0):
	if board_name is None:
		raise PermissionDenied()
	try:
		board = Board.objects.get(name=board_name)
		article = Article.objects.get(board=board, num=article_num, deleted=False)
	except:
		raise Http404()

	if article.board != board:
		raise Http404()
		
	content = request.POST.get('content', '')
	writer_name = get_writer_name(board, article, request.user)
	comment = Comment.objects.create(user=request.user, content=content, article=article, writer_name=writer_name)

	return HttpResponseRedirect('/board/%s/view/%d/'%(article.board.name, article.num))


@login_required
def board_article_modify(request, board_name=None, article_num=0):
	if board_name is None:
		raise PermissionDenied()
	try:
		board = Board.objects.get(name=board_name)
		article = Article.objects.get(board=board, num=article_num, deleted=False)
	except:
		raise Http404()

	if request.method == 'GET':
		return render_to_response('board/article_write.html', RequestContext(request, {'board': board, 'article': article}));

	title = request.POST.get('title', '')
	content = request.POST.get('content', '')
	is_important = request.POST.get('is_important', False) and request.user.is_staff
	article.title = title
	article.content = get_safe(content)
	article.is_important = is_important
	article.save()
	return HttpResponseRedirect('/board/%s/view/%d/'%(board.name, article.num))

