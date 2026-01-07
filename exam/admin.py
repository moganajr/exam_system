from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
import uuid
from django.utils import timezone
from .models import (
    ExamResult,
    EnglishQuestion,
    MathQuestion,
    PaymentClearance,
    ClearanceLog
)
from .signals import send_clearance


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
    list_filter = ("subject", "status", "created_at")
    search_fields = ("student_name", "student_email")
    ordering = ("-created_at",)
    list_per_page = 25


# ================= ENGLISH QUESTION BANK =================
@admin.register(EnglishQuestion)
class EnglishQuestionAdmin(ImportExportModelAdmin):
    list_display = ("question", "answer")
    search_fields = ("question",)
    list_per_page = 25


# ================= MATH QUESTION BANK =================
@admin.register(MathQuestion)
class MathQuestionAdmin(ImportExportModelAdmin):
    list_display = ("question", "answer")
    search_fields = ("question",)
    list_per_page = 25


# ================= PAYMENT CLEARANCE ADMIN =================
@admin.register(PaymentClearance)
class PaymentClearanceAdmin(admin.ModelAdmin):
    list_display = (
        "student_email",
        "exam_type",
        "code",
        "is_used",
        "email_sent",
        "last_email_at",
        "created_at",
    )

    search_fields = ("student_email", "code")
    list_filter = ("exam_type", "is_used", "email_sent")
    readonly_fields = ("code", "created_at", "used_at", "last_email_at")
    list_per_page = 25

    # ---------- RESET CODE ----------
    def reset_code(self, request, queryset):
        for obj in queryset:
            old_code = obj.code
            obj.code = uuid.uuid4().hex[:8].upper()
            obj.is_used = False
            obj.save()

            ClearanceLog.objects.create(
                student_email=obj.student_email,
                action="CODE_RESET",
                details=f"Old: {old_code} → New: {obj.code}"
            )

    reset_code.short_description = "Reset Clearance Code"


    # ---------- RESEND EMAIL ----------
    def resend_email(self, request, queryset):
        for obj in queryset:
            send_clearance(obj)

            ClearanceLog.objects.create(
                student_email=obj.student_email,
                action="EMAIL_RESENT",
                details=f"Resent Code: {obj.code}"
            )

    resend_email.short_description = "Resend Clearance Email"


    actions = ["reset_code", "resend_email"]



# ================= PAYMENT LOG ADMIN =================
@admin.register(ClearanceLog)
class ClearanceLogAdmin(admin.ModelAdmin):
    list_display = ("student_email", "action", "details", "timestamp")
    search_fields = ("student_email", "action")
    ordering = ("-timestamp",)
    list_per_page = 30
