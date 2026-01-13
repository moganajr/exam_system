from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
import uuid
from django.utils import timezone
from .models import (
    ExamResult,
    EnglishQuestion,
    MathQuestion,
    PaymentClearance,
    ClearanceLog,
    ExamSession,
)
from .signals import send_clearance
from django.utils.safestring import mark_safe
import json
from django.core import signing
from django.conf import settings
from django.http import HttpResponse
from .models import ExamConfig, ResumeLog


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


# ================= EXAM SESSION ADMIN =================
@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = (
        "student_email",
        "exam_type",
        "is_completed",
        "started_at",
        "last_saved",
        "question_count",
        "resume_link_button",
    )
    list_filter = ("exam_type", "is_completed", "started_at")
    search_fields = ("student_email",)
    readonly_fields = ("started_at", "last_saved")
    ordering = ("-last_saved",)
    list_per_page = 40

    def question_count(self, obj):
        try:
            return len(obj.question_ids or [])
        except Exception:
            return 0
    question_count.short_description = "# Questions"

    def resume_link_button(self, obj):
        try:
            url = f"generate_resume/{obj.id}/"
            full = f"/admin/exam/examsession/{obj.id}/change/"
            # link to custom admin view
            return mark_safe(f"<a class='button' href='{url}'>Generate Link</a>")
        except Exception:
            return ""
    resume_link_button.short_description = "Generate Link"

    def question_ids_json(self, obj):
        try:
            return mark_safe(f"<pre>{json.dumps(obj.question_ids, indent=2)}</pre>")
        except Exception:
            return ""
    question_ids_json.short_description = "Question IDs"

    def answers_json(self, obj):
        try:
            return mark_safe(f"<pre>{json.dumps(obj.answers, indent=2)}</pre>")
        except Exception:
            return ""
    answers_json.short_description = "Answers"
    readonly_fields = ("started_at", "last_saved", "question_ids_json", "answers_json")

    # ---------- ACTIONS ----------
    def mark_completed(self, request, queryset):
        for obj in queryset:
            obj.mark_completed()
    mark_completed.short_description = "Mark selected sessions as completed"

    def clear_answers(self, request, queryset):
        for obj in queryset:
            obj.answers = {}
            obj.save()
    clear_answers.short_description = "Clear saved answers for selected sessions"

    def delete_sessions(self, request, queryset):
        for obj in queryset:
            obj.delete()
    delete_sessions.short_description = "Delete selected sessions"

    actions = ["mark_completed", "clear_answers", "delete_sessions"]
    # ---------- EXPORT / RESUME ACTIONS ----------
    def export_sessions(self, request, queryset):
        """Export selected sessions as a JSON attachment."""
        rows = []
        for obj in queryset:
            rows.append({
                "id": obj.id,
                "student_email": obj.student_email,
                "exam_type": obj.exam_type,
                "question_ids": obj.question_ids,
                "q_options_order": obj.q_options_order,
                "answers": obj.answers,
                "started_at": obj.started_at.isoformat(),
                "last_saved": obj.last_saved.isoformat(),
                "is_completed": obj.is_completed,
            })

        import datetime
        resp = HttpResponse(
            json.dumps(rows, indent=2),
            content_type="application/json"
        )
        resp["Content-Disposition"] = f"attachment; filename=exam_sessions_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
        return resp
    export_sessions.short_description = "Export selected sessions to JSON"

    def generate_resume_link(self, request, queryset):
        """Generate signed resume links (one-time) for selected sessions."""
        links = []
        signer = signing.TimestampSigner()
        # prefer admin-configured expiry from ExamConfig singleton
        cfg = ExamConfig.objects.first()
        expiry = cfg.resume_link_expiry_seconds if cfg else getattr(settings, "RESUME_LINK_EXPIRY_SECONDS", 3600)
        for obj in queryset:
            token = signer.sign(json.dumps({"session_id": obj.id}))
            # build absolute URL
            url = request.build_absolute_uri(f"/exam/resume/{token}/")
            links.append({"email": obj.student_email, "url": url, "expiry_seconds": expiry})

            # Audit log
            try:
                ResumeLog.objects.create(student_email=obj.student_email, action="GENERATED", details=f"Generated link for session {obj.id}")
            except Exception:
                pass

        content = json.dumps(links, indent=2)
        resp = HttpResponse(content, content_type="application/json")
        resp["Content-Disposition"] = "attachment; filename=resume_links.json"
        return resp
    generate_resume_link.short_description = "Generate resume links for selected sessions"

    actions = ["mark_completed", "clear_answers", "delete_sessions", "export_sessions", "generate_resume_link"]


@admin.register(ExamConfig)
class ExamConfigAdmin(admin.ModelAdmin):
    list_display = ("resume_link_expiry_seconds",)
    fieldsets = ((None, {"fields": ("resume_link_expiry_seconds",)}),)

    def has_add_permission(self, request):
        # Allow adding only if no config exists (singleton-like)
        return not ExamConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion from admin to keep one config present
        return False

    # Add custom admin URLs for per-row resume link generation
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('generate_resume/<int:session_id>/', self.admin_site.admin_view(self.generate_resume_for_session), name='generate_resume_for_session'),
        ]
        return custom_urls + urls

    def generate_resume_for_session(self, request, session_id):
        try:
            obj = ExamSession.objects.get(pk=session_id)
        except ExamSession.DoesNotExist:
            return HttpResponse('Session not found', status=404)

        signer = signing.TimestampSigner()
        cfg = ExamConfig.objects.first()
        expiry = cfg.resume_link_expiry_seconds if cfg else getattr(settings, "RESUME_LINK_EXPIRY_SECONDS", 3600)
        token = signer.sign(json.dumps({"session_id": obj.id}))
        url = request.build_absolute_uri(f"/exam/resume/{token}/")

        # Audit log
        try:
            ResumeLog.objects.create(student_email=obj.student_email, action="GENERATED", details=f"Generated link via admin view for session {obj.id}")
        except Exception:
            pass

        # Render a simple page with the link
        html = f"<html><body><h2>Resume Link</h2><p><a href='{url}' target='_blank'>{url}</a></p><p>Expires in {expiry} seconds.</p><p><a href='..'>Back</a></p></body></html>"
        return HttpResponse(html)
