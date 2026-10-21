from django.urls import path

from . import views


app_name = 'cheatsheets'

urlpatterns = [
    path('', views.CheatsheetListView.as_view(), name='list'),
    path('<slug:course>/', views.CheatsheetDetailView.as_view(), name='detail'),
]
