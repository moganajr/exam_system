from django.db import models

class ExamResult(models.Model):
    student_name = models.CharField(max_length=100)
    student_email = models.EmailField()
    score = models.IntegerField()
    total = models.IntegerField()
    percentage = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.score}/{self.total}"
