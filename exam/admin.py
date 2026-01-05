from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import ExamResult


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
