from django.core.management.base import BaseCommand
from exam.models import MathQuestion
from exam.views import math_questions


class Command(BaseCommand):
    help = "Load Math exam questions into database"

    def handle(self, *args, **kwargs):
        MathQuestion.objects.all().delete()
        self.stdout.write("Deleted old Math questions")

        for key, q in math_questions.items():
            MathQuestion.objects.create(
                question=q["q"],
                option_a=q["options"]["A"],
                option_b=q["options"]["B"],
                option_c=q["options"]["C"],
                option_d=q["options"]["D"],
                answer=q["answer"]
            )

        self.stdout.write(self.style.SUCCESS("Math questions loaded successfully!"))
