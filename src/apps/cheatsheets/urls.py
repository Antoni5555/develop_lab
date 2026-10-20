from django.urls import path

from . import views


app_name = 'cheatsheets'

urlpatterns = [
    path('', views.CheatsheetListView.as_view(), name='list'),
]
