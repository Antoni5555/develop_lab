from django.urls import path

from . import api


app_name = 'notes'

urlpatterns = [
    path('', api.NoteListView.as_view(), name='list'),
    path('<int:pk>/', api.NoteDetailView.as_view(), name='detail'),
]
