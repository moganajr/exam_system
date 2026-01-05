from django.contrib import admin
from django.urls import path
from exam.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
]
