from django.urls import path
from . import views

urlpatterns = [
    path('', views.select_exam, name='select_exam'),
    path('english/', views.home, name='english_exam'),
    path('math/', views.math_exam, name='math_exam'),
]
