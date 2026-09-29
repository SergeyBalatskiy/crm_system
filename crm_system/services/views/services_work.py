from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from storage.models import StorageInfo
from django.shortcuts import render
from django.db.models import Q, TextField, F
from django.views import View
from django.db.models.functions import Cast
from datetime import timedelta
from datetime import datetime

class ShowAndCreateServicesWork(View):
    def get(self, request, *args, **kwargs):
        ...

    def post(self, request, *args, **kwargs):
        ...