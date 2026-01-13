from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from exam import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),

    path('admin/', admin.site.urls),
    path('admin/active_sessions_count/', views.admin_active_sessions_count, name='admin_active_sessions_count'),

    path('verify-payment/', views.verify_payment, name='verify_payment'),

    path('select/', views.select_exam, name='select_exam'),

    path('english/', views.english_exam, name='english_exam'),

    path('math/', views.math_exam, name='math_exam'),
]
