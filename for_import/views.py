from django.db import models
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, HttpResponse
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import DetailView, ListView
from products.models import Category


