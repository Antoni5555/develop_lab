from django.urls import path

from . import views


app_name = 'trainers'

urlpatterns = [
    path('playground/', views.PlaygroundView.as_view(), name='playground'),
]
