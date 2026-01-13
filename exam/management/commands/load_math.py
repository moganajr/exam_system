from django.core.management.base import BaseCommand
from exam.models import MathQuestion
import random


def _make_options(correct, wrongs):
    """Return a dict of options A-D and the correct letter."""
    choices = [str(correct)] + [str(w) for w in wrongs]
    random.shuffle(choices)
    mapping = {k: v for k, v in zip(["A", "B", "C", "D"], choices)}
    # find correct key
    for k, v in mapping.items():
        if str(v) == str(correct):
            return mapping, k
    return mapping, "A"


class Command(BaseCommand):
    help = "Generate and load 100 Math exam questions into database"

    def handle(self, *args, **kwargs):
        MathQuestion.objects.all().delete()
        self.stdout.write("Deleted old Math questions")

        questions = []

        for i in range(1, 101):
            # Cycle through a set of question templates
            t = i % 10

            if t == 1:
                # simple addition
                a = random.randint(5, 90)
                b = random.randint(5, 90)
                q = f"What is {a} + {b}?"
                correct = a + b
                wrongs = [correct + random.choice([-3, -2, 2, 3]), correct + random.choice([4, -4, 5]) , correct + random.choice([6, -6])]

            elif t == 2:
                # subtraction
                a = random.randint(30, 120)
                b = random.randint(1, 29)
                q = f"What is {a} − {b}?"
                correct = a - b
                wrongs = [correct + random.choice([1,2,3]), correct + random.choice([-2, -5]), correct + random.choice([5,10])]

            elif t == 3:
                # multiplication
                a = random.randint(2, 20)
                b = random.randint(2, 12)
                q = f"What is {a} × {b}?"
                correct = a * b
                wrongs = [correct + random.choice([a, b, -a]), correct + random.choice([2, -2]), max(1, correct - random.randint(3,8))]

            elif t == 4:
                # division with integer result
                b = random.randint(2, 12)
                correct = random.randint(2, 15)
                a = b * correct
                q = f"What is {a} ÷ {b}?"
                wrongs = [correct + 1, max(1, correct - 1), correct + random.choice([2,3])]

            elif t == 5:
                # simple linear equation ax + b = c
                x = random.randint(1, 12)
                a = random.randint(1, 6)
                b = random.randint(-10, 10)
                c = a * x + b
                q = f"Solve for x: {a}x + ({b}) = {c}"
                correct = x
                wrongs = [x + 1, max(0, x - 1), x + 2]

            elif t == 6:
                # percentages
                base = random.choice([50, 80, 120, 200, 360])
                p = random.choice([10, 20, 25, 50])
                q = f"What is {p}% of {base}?"
                correct = int(base * p / 100)
                wrongs = [correct + random.choice([1,2,3]), max(1, correct - random.choice([1,2,3])), correct + random.choice([5,10])]

            elif t == 7:
                # simple fraction addition
                a, b = random.randint(1, 6), random.randint(1, 6)
                c, d = random.randint(1, 6), random.randint(1, 6)
                num = a * d + b * c
                den = b * d
                # reduce
                from math import gcd
                g = gcd(num, den)
                correct_num, correct_den = num // g, den // g
                q = f"Compute: {a}/{b} + {c}/{d} (in lowest terms)"
                correct = f"{correct_num}/{correct_den}"
                wrongs = [f"{max(1, correct_num-1)}/{correct_den}", f"{correct_num}/{max(1, correct_den-1)}", f"{correct_num+1}/{correct_den}"]

            elif t == 8:
                # geometry area of rectangle
                l = random.randint(2, 20)
                w = random.randint(2, 20)
                q = f"Area of rectangle with length {l} and width {w} (in square units)" 
                correct = l * w
                wrongs = [correct + random.choice([1,2,3]), max(1, correct - random.choice([2,4])), correct + random.choice([5,10])]

            elif t == 9:
                # pythagorean simple
                triples = [(3,4,5),(5,12,13),(8,15,17),(7,24,25)]
                a,b,c = random.choice(triples)
                # ask hypotenuse
                q = f"In a right triangle with legs {a} and {b}, the hypotenuse is:" 
                correct = c
                wrongs = [c+1, max(1,c-1), c+2]

            else:
                # simple average
                nums = [random.randint(1,30) for _ in range(5)]
                q = f"Find the mean of {', '.join(map(str, nums))}."
                correct = round(sum(nums)/len(nums), 2)
                # if integer, show as int
                if isinstance(correct, float) and correct.is_integer():
                    correct = int(correct)
                wrongs = [round(correct + random.choice([-2,-1,1,2]), 2) if isinstance(correct, float) else correct + random.choice([1,2,-1]) for _ in range(3)]

            # build options and answer
            opts, ans = _make_options(correct, wrongs)

            MathQuestion.objects.create(
                question=q,
                option_a=opts["A"],
                option_b=opts["B"],
                option_c=opts["C"],
                option_d=opts["D"],
                answer=ans,
            )

        self.stdout.write(self.style.SUCCESS("100 Math questions generated and loaded successfully!"))
