from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('querie/<str:location>/<str:query>/', views.querie, name='querie_detail'),
]
