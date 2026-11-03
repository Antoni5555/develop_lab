from django.urls import path

from . import api


app_name = 'reports'

urlpatterns = [
    path('', api.ReportListView.as_view(), name='list'),
]
