from django.core.management.base import BaseCommand
from exam.models import EnglishQuestion
from exam.views import questions


class Command(BaseCommand):
    help = "Load English exam questions into database"

    def handle(self, *args, **kwargs):
        EnglishQuestion.objects.all().delete()
        self.stdout.write("Deleted old English questions")

        for key, q in questions.items():
            EnglishQuestion.objects.create(
                question=q["q"],
                option_a=q["options"]["A"],
                option_b=q["options"]["B"],
                option_c=q["options"]["C"],
                option_d=q["options"]["D"],
                answer=q["answer"]
            )

        self.stdout.write(self.style.SUCCESS("English questions loaded successfully!"))
