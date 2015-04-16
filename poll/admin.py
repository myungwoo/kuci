from django.contrib import admin

from models import *

# Register your models here.
admin.site.register(Poll)
admin.site.register(Choice)
admin.site.register(UserChoiceInfo)
admin.site.register(MemberVoteInfo)