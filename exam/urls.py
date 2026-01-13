from django.shortcuts import redirect
from django.contrib import admin
from django.urls import path
from exam import views

urlpatterns = [
    path('', lambda request: redirect('verify_payment'), name='home'),
    path('admin/', admin.site.urls),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('select/', views.select_exam, name='select_exam'),
    path('english/', views.english_exam, name='english_exam'),
    path('math/', views.math_exam, name='math_exam'),
    path('autosave/', views.autosave_exam, name='autosave_exam'),
    path('resume/<str:token>/', views.resume_session, name='resume_session'),
]
