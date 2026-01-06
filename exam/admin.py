from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import ExamResult, EnglishQuestion, MathQuestion


# ================= EXAM RESULT ADMIN =================
@admin.register(ExamResult)
class ExamResultAdmin(ImportExportModelAdmin):
    list_display = (
        "student_name",
        "student_email",
        "subject",
        "score",
        "total",
        "percentage",
        "status",
        "created_at",
    )

    list_filter = (
        "subject",
        "status",
        "created_at",
    )

    search_fields = (
        "student_name",
        "student_email",
    )

    ordering = ("-created_at",)
    list_per_page = 25


# ================= ENGLISH QUESTION BANK ADMIN =================
@admin.register(EnglishQuestion)
class EnglishQuestionAdmin(ImportExportModelAdmin):
    list_display = ("question", "answer")
    search_fields = ("question",)
    list_per_page = 25


# ================= MATH QUESTION BANK ADMIN =================
@admin.register(MathQuestion)
class MathQuestionAdmin(ImportExportModelAdmin):
    list_display = ("question", "answer")
    search_fields = ("question",)
    list_per_page = 25

from django.contrib import admin
from .models import PaymentClearance

@admin.register(PaymentClearance)
class PaymentClearanceAdmin(admin.ModelAdmin):
    list_display = ("student_email", "exam_type", "code", "is_used", "created_at")
    readonly_fields = ("code", "is_used", "created_at", "used_at")
