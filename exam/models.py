from django.db import models
import uuid
from django.utils import timezone


# ================= EXAM RESULT MODEL =================
class ExamResult(models.Model):
    student_name = models.CharField(max_length=200)
    student_email = models.EmailField()
    subject = models.CharField(max_length=50)
    score = models.IntegerField()
    total = models.IntegerField()
    percentage = models.FloatField()
    status = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.subject}"


# ================= ENGLISH QUESTION BANK =================
class EnglishQuestion(models.Model):
    question = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    answer = models.CharField(max_length=1)

    def __str__(self):
        return self.question[:60]


# ================= MATH QUESTION BANK =================
class MathQuestion(models.Model):
    question = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    answer = models.CharField(max_length=1)

    def __str__(self):
        return self.question[:60]


# ================= CODE GENERATOR =================
def generate_code():
    return uuid.uuid4().hex[:8].upper()     # Example: 8AF73C4D


# ================= PAYMENT CLEARANCE =================
class PaymentClearance(models.Model):
    student_email = models.EmailField()

    exam_type = models.CharField(max_length=20, choices=[
        ("ENGLISH", "English"),
        ("MATH", "Math"),
        ("BOTH", "Both"),
    ])

    code = models.CharField(max_length=20, unique=True, default=generate_code)

    # Usage
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    # Email tracking
    email_sent = models.BooleanField(default=False)
    last_email_at = models.DateTimeField(null=True, blank=True)

    def mark_used(self):
        """Securely mark clearance as used"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.student_email} - {self.exam_type}"


# ================= SECURITY / AUDIT LOGS =================
class ClearanceLog(models.Model):
    student_email = models.EmailField()
    action = models.CharField(max_length=50)  
    # CREATED / EMAIL_SENT / EMAIL_FAILED / VERIFIED / USED / RESET
    details = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_email} - {self.action}"


# ===================== EXAM SESSION (PERSISTENT) =====================
class ExamSession(models.Model):
    student_email = models.EmailField()

    exam_type = models.CharField(max_length=10, choices=[
        ("ENGLISH", "English"),
        ("MATH", "Math"),
    ])

    question_ids = models.JSONField(default=list)
    q_options_order = models.JSONField(default=dict)
    answers = models.JSONField(default=dict, blank=True)

    started_at = models.DateTimeField(auto_now_add=True)
    last_saved = models.DateTimeField(auto_now=True)

    is_completed = models.BooleanField(default=False)

    def mark_completed(self):
        self.is_completed = True
        self.save(update_fields=["is_completed", "last_saved"])

    def __str__(self):
        return f"{self.student_email} - {self.exam_type} - {'DONE' if self.is_completed else 'ACTIVE'}"


# ===================== EXAM CONFIG (singleton-like) =====================
class ExamConfig(models.Model):
    resume_link_expiry_seconds = models.IntegerField(default=3600, help_text="Expiry for generated resume links in seconds")

    def __str__(self):
        return f"Exam Config"


# ===================== RESUME AUDIT LOG =====================
class ResumeLog(models.Model):
    student_email = models.EmailField()
    action = models.CharField(max_length=50)  # GENERATED / USED
    details = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_email} - {self.action}"
