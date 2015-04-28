from django.conf.urls import patterns, include, url
from django.contrib import admin

from members.views import *
from board.views import *
from poll.views import *
from rent.views import *
from views import *

admin.autodiscover()

handler403 = views_403
handler404 = views_404
handler500 = views_500


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'kuci.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views_calendar),

    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),

    url(r'^privacy/$', members_privacy),

	url(r'^register/$', members_register),
    url(r'^change_info/$', members_change_info),
    url(r'^find_id_pw/$', members_find_id_pw),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^board/(?P<board_name>\w+)/$', board_article_list),
    url(r'^board/(?P<board_name>\w+)/page(?P<page_num>\d+)/$', board_article_list),
    url(r'^board/(?P<board_name>\w+)/view/(?P<article_num>\d+)/$', board_article_view),
    url(r'^board/(?P<board_name>\w+)/modify/(?P<article_num>\d+)/$', board_article_modify),
    url(r'^board/(?P<board_name>\w+)/write/$', board_article_write),
    url(r'^board/(?P<board_name>\w+)/delete/(?P<article_num>\d+)/$', board_article_delete),
    url(r'^board/(?P<board_name>\w+)/comment/delete/(?P<comment_id>\d+)/$', board_comment_delete),
    url(r'^board/(?P<board_name>\w+)/comment/write/(?P<article_num>\d+)/$', board_comment_write),

    url(r'^poll/$', poll_list),
    url(r'^poll/(?P<poll_name>\w+)/$', poll_view),
    url(r'^poll/(?P<poll_name>\w+)/result/$', poll_result),
    url(r'^poll/(?P<poll_name>\w+)/offline/$', poll_offline),
    url(r'^poll/(?P<poll_name>\w+)/voter_list/$', poll_voter_list),
    url(r'^poll/(?P<poll_name>\w+)/delete_offline_voter/(?P<info_id>\d+)/$', poll_delete_offline_voter),

    url(r'^rent/$', rent_main),

    url(r'^ajax/poll/(?P<poll_name>\w+)/make_security/$', poll_make_security),
    url(r'^ajax/poll/(?P<poll_name>\w+)/code_check/$', poll_code_check),
    url(r'^ajax/poll/(?P<poll_name>\w+)/check_voted/$', poll_check_voted),
    url(r'^ajax/poll/get_voters/$', poll_get_voters),
    url(r'^ajax/members/make_security/$', members_make_security), 
    url(r'^ajax/members/code_check/$', members_code_check),
    url(r'^ajax/members/username_duplication_check/$', members_username_duplication_check),
    url(r'^ajax/members/send_verify_email/$', members_send_verify_email),
    url(r'^ajax/members/check_verify_code/$', members_check_verify_code),
    url(r'^ajax/members/find_id/$', members_ajax_find_id),
    url(r'^ajax/members/find_pw/$', members_ajax_find_pw),
    url(r'^ajax/rent/get_content/$', rent_ajax_get_content),
    url(r'^ajax/rent/get_rentinfo/$', rent_ajax_get_rentinfo),
    url(r'^ajax/rent/delete_rentinfo/$', rent_ajax_delete_rentinfo),
    url(r'^ajax/rent/write_rentinfo/$', rent_ajax_write_rentinfo),

    url(r'^ajax/upload_image/$', board_upload_image),
    url(r'^ajax/upload_file/$', board_upload_file),

    url(r'^uploads/(?P<path>.*)$', board_upload_serve),
    url(r'^static/(?P<path>.*)$', views_static_serve),
)
