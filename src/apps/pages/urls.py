from django.urls import path

from . import views


app_name = 'pages'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('privacy/', views.LegalView.as_view(
        template_name='legal/privacy.html'), name='privacy'),
    path('personal-data-consent/', views.LegalView.as_view(
        template_name='legal/consent.html'), name='consent'),
]
