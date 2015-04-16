
from models import *

def user_vote_permission(poll, user):
	try:
		member = Member.objects.get(user=user)
	except:
		return False
	if member.type == 2 and not poll.regular_only:
		return True
	if member.type != 1:
		return False
	return True

def member_vote_permission(poll, member):
	if member.type == 2 and not poll.regular_only:
		return True
	if member.type != 1:
		return False
	return True

def is_user_voted(poll, user):
	if not user_vote_permission(poll, user):
		return False
	try:
		member = Member.objects.get(user=user)
		mvi = MemberVoteInfo.objects.get(member=member, poll=poll)
	except:
		return False
	return True

def is_member_voted(poll, member):
	if not member_vote_permission(poll, member):
		return False
	try:
		mvi = MemberVoteInfo.objects.get(member=member, poll=poll)
	except:
		return False
	return True

def get_users_poll_status(poll, user):
	if not user_vote_permission(poll, user):
		return 0
	elif is_user_voted(poll, user):
		return 2
	return 1