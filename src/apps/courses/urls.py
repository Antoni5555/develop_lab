from django.urls import path

from . import views


app_name = 'courses'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='list'),
    path('<slug:course>/', views.CourseDetailView.as_view(), name='detail'),
    path(
        '<slug:course>/<slug:section>/<slug:topic>/',
        views.LessonView.as_view(), name='lesson',
    ),
]
