import requests, json, math

from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views import View

from .custom import count_page
from .models import FtUser


# Create your views here.
class FtApi:
	ft_access_token = None
	ft_oauth_url = "https://api.intra.42.fr/oauth/token"
	ft_api_url = "https://api.intra.42.fr/v2/"
	update_branch = None

	def __init__(self, UpdateBranch=None):
		self.ft_uid_key = settings.FT_UID_KEY
		self.ft_secret_key = settings.FT_SECRET_KEY
		self.update_branch = UpdateBranch if UpdateBranch else None

	def get_access_token(self):
		oauth_data = {
			'grant_type': 'client_credentials',
			'client_id': self.ft_uid_key,
			'client_secret': self.ft_secret_key,
		}
		self.ft_access_token = requests.post(self.ft_oauth_url, data=oauth_data).json()['access_token']
		return self.ft_access_token

	def get_data(self, url, page=1, per_page=100, sort=None):
		params = {
			'access_token' : self.get_access_token(),
			'page' : page if page else '',
			'per_page' : per_page if per_page else '',
			'sort' : sort if sort else '',
		}
		return requests.get(f'{self.ft_api_url}{url}', params=params).json()


class SuperUserCheckMixin(UserPassesTestMixin, View):
	def test_func(self):
		return self.request.user.is_superuser


class ManagePage(SuperUserCheckMixin, TemplateView):
	template_name = "managepage.html"


class MakeFtUser(View):
	def post(self, request):
		ft_api = FtApi()
		page = count_page(int(ft_api.get_data(url="campus/29").json()["users_count"]))
		crawlings = [ft_api.get_data(url="campus/29/users", page=x, per_page=100, sort="login") for x in page]
		for crawling in crawlings:
			crawling.