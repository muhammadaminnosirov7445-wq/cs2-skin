from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('open/<int:case_id>/', views.open_case, name='open_case'),
]

