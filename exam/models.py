from django.db import models

class ExamResult(models.Model):
    student_name = models.CharField(max_length=200)
    student_email = models.EmailField()
    subject = models.CharField(max_length=50, default="Unknown")
    score = models.IntegerField()
    total = models.IntegerField()
    percentage = models.FloatField()
    status = models.CharField(max_length=20, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.subject} ({self.percentage}%)"
