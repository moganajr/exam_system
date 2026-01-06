from django.db import models


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

import uuid
from django.db import models

def generate_code():
    return str(uuid.uuid4()).split("-")[0].upper()  # e.g: 9AF32C

class PaymentClearance(models.Model):
    student_email = models.EmailField()
    exam_type = models.CharField(max_length=20, choices=[
        ("ENGLISH","English"),
        ("MATH","Math"),
        ("BOTH","Both")
    ])
    
    code = models.CharField(max_length=20, unique=True, default=generate_code)
    
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student_email} - {self.exam_type}"

import uuid
from django.db import models

def generate_code():
    return str(uuid.uuid4()).split("-")[0].upper()

class PaymentClearance(models.Model):
    student_email = models.EmailField(unique=True)
    
    exam_type = models.CharField(max_length=20, choices=[
        ("ENGLISH", "English"),
        ("MATH", "Math"),
        ("BOTH", "Both")
    ])
    
    code = models.CharField(max_length=20, unique=True, default=generate_code)

    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student_email} - {self.exam_type}"
