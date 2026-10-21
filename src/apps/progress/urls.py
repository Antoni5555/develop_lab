from django.urls import path

from . import api


app_name = 'progress'

urlpatterns = [
    path('solved/', api.SolvedView.as_view(), name='solved'),
    path('import/', api.ImportView.as_view(), name='import'),
]
