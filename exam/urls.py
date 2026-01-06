from django.urls import path
from . import views

urlpatterns = [
    path("", views.verify_payment, name="verify_payment"),
    path("select/", views.select_exam, name="select_exam"),
    path("english/", views.english_exam, name="english_exam"),
    path("math/", views.math_exam, name="math_exam"),
]
