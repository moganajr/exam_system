from django.shortcuts import render
from .models import ExamResult


# ===================== SUBJECT SELECTION =====================
def select_exam(request):
    return render(request, "select_exam.html")


# ===================== ENGLISH QUESTIONS =====================
questions = {
    # ---------- GRAMMAR ----------
    1: {"q": "Identify the correct sentence.",
        "options": {"A": "She don’t like apples.",
                    "B": "She doesn’t likes apples.",
                    "C": "She doesn’t like apples.",
                    "D": "She don’t likes apples."},
        "answer": "C"},
    2: {"q": "Which word is a preposition?",
        "options": {"A": "Quickly", "B": "Beneath", "C": "Laugh", "D": "Strong"},
        "answer": "B"},
    3: {"q": "Choose the grammatically correct sentence.",
        "options": {"A": "Each of the boys have a book.",
                    "B": "Each of the boys has a book.",
                    "C": "Each of the boy have books.",
                    "D": "Each boys has book."},
        "answer": "B"},
    4: {"q": "Neither John nor his friends brought ___ books.",
        "options": {"A": "his", "B": "her", "C": "their", "D": "its"},
        "answer": "C"},
    5: {"q": "Which sentence is correct?",
        "options": {"A": "The informations are useful.",
                    "B": "The information is useful.",
                    "C": "The informations is useful.",
                    "D": "Information are useful."},
        "answer": "B"},

    # ---------- TENSES ----------
    6: {"q": "By this time tomorrow, we ___ our exams.",
        "options": {"A": "will finish", "B": "have finished",
                    "C": "will have finished", "D": "finished"},
        "answer": "C"},
    7: {"q": "Correct sentence:",
        "options": {"A": "He has went to school.", "B": "He has gone to school.",
                    "C": "He have gone to school.", "D": "He going to school."},
        "answer": "B"},
    8: {"q": "She ___ when I arrived.",
        "options": {"A": "was sleeping", "B": "slept",
                    "C": "is sleeping", "D": "has slept"},
        "answer": "A"},
    9: {"q": "If I ___ enough money, I would travel.",
        "options": {"A": "have", "B": "had", "C": "will have", "D": "would have"},
        "answer": "B"},
    10: {"q": "Choose the correct sentence.",
         "options": {"A": "I am used to wake up early.",
                     "B": "I used to waking up early.",
                     "C": "I am used to waking up early.",
                     "D": "I used to wake up early now."},
         "answer": "C"},

    # ---------- SENTENCE STRUCTURE ----------
    11: {"q": "Although he was tired, he finished the work. Type?",
         "options": {"A": "Simple", "B": "Compound", "C": "Complex", "D": "Fragment"},
         "answer": "C"},
    12: {"q": "Find the error: She is the most smartest girl.",
         "options": {"A": "She", "B": "most", "C": "smartest", "D": "girl"},
         "answer": "B"},
    13: {"q": "Correct punctuation: Its raining we should stay inside",
         "options": {"A": "It’s raining; we should stay inside.",
                     "B": "Its raining; we should stay inside.",
                     "C": "It’s raining we should stay inside.",
                     "D": "Its raining, we should stay inside."},
         "answer": "A"},
    14: {"q": "Choose the correct sentence.",
         "options": {"A": "The boy who was crying loudly left the room.",
                     "B": "The boy left the room who was crying loudly.",
                     "C": "Loudly crying boy left room.",
                     "D": "The left room boy loudly crying."},
         "answer": "A"},
    15: {"q": "Identify error: He asked me where was I going.",
         "options": {"A": "He", "B": "asked", "C": "was I", "D": "going"},
         "answer": "C"},

    # ---------- VOCABULARY ----------
    16: {"q": "Synonym of abundant:",
         "options": {"A": "scarce", "B": "plenty", "C": "few", "D": "limited"},
         "answer": "B"},
    17: {"q": "Antonym of victory:",
         "options": {"A": "win", "B": "conquer", "C": "defeat", "D": "triumph"},
         "answer": "C"},
    18: {"q": "Correct word: She has a strong ___ in education.",
         "options": {"A": "believe", "B": "believing", "C": "belief", "D": "beliefs"},
         "answer": "C"},
    19: {"q": "He kicked the bucket means:",
         "options": {"A": "He kicked something", "B": "He ran away",
                     "C": "He died", "D": "He got angry"},
         "answer": "C"},
    20: {"q": "Correct spelling:",
         "options": {"A": "Accomodation", "B": "Acommodation",
                     "C": "Accommondation", "D": "Accommodation"},
         "answer": "D"},

    # ---------- COMPREHENSION ----------
    21: {"q": "Education helps people:",
         "options": {"A": "only helps rich", "B": "not important",
                     "C": "contribute to society", "D": "only provides jobs"},
         "answer": "C"},
    22: {"q": "Meaning of empowers:",
         "options": {"A": "weakens", "B": "strengthens", "C": "punishes", "D": "confuses"},
         "answer": "B"},
    23: {"q": "Education helps people:",
         "options": {"A": "avoid school", "B": "think critically",
                     "C": "travel abroad", "D": "become politicians"},
         "answer": "B"},
    24: {"q": "Tone is:",
         "options": {"A": "negative", "B": "neutral", "C": "positive", "D": "angry"},
         "answer": "C"},
    25: {"q": "Best title:",
         "options": {"A": "Problems of Education", "B": "Education and Society",
                     "C": "Students Fail", "D": "Education is useless"},
         "answer": "B"},

    # ---------- COMPOSITION ----------
    26: {"q": "Best topic sentence:",
         "options": {"A": "Many people like beach.",
                     "B": "Protecting the environment is essential.",
                     "C": "Pollution is everywhere.",
                     "D": "Trees are green."},
         "answer": "B"},
    27: {"q": "Best conclusion:",
         "options": {"A": "Everyone must help save the planet.",
                     "B": "Pollution is bad.", "C": "Water is important.", "D": "The essay ends."},
         "answer": "A"},
    28: {"q": "Coherent sentence:",
         "options": {"A": "Because the earth needs save.",
                     "B": "Earth saving need.",
                     "C": "The earth needs protection.",
                     "D": "Earth need protect."},
         "answer": "C"},
    29: {"q": "Best transition word: ___, climate change affects millions.",
         "options": {"A": "However", "B": "Therefore", "C": "Firstly", "D": "Meanwhile"},
         "answer": "C"},
    30: {"q": "Formal sentence:",
         "options": {"A": "This stuff is bad.",
                     "B": "It’s kinda serious.",
                     "C": "This issue requires urgent attention.",
                     "D": "Wow!"},
         "answer": "C"},

    # ---------- LOGIC ----------
    31: {"q": "David is a writer. All writers are creative.",
         "options": {"A": "not creative", "B": "maybe creative",
                     "C": "David is creative", "D": "unknown"},
         "answer": "C"},
    32: {"q": "If all teachers have degrees and Sarah has none:",
         "options": {"A": "Sarah is a teacher", "B": "Sarah is not a teacher",
                     "C": "maybe", "D": "none"},
         "answer": "B"},
    33: {"q": "cat, dog, lion, tiger are:",
         "options": {"A": "birds", "B": "reptiles", "C": "mammals", "D": "fish"},
         "answer": "C"},
    34: {"q": "If A implies B, and B did not happen:",
         "options": {"A": "A happened", "B": "A did not happen",
                     "C": "maybe happened", "D": "cannot conclude"},
         "answer": "B"},
    35: {"q": "Which does NOT belong? book, pen, pencil, airplane",
         "options": {"A": "book", "B": "pen", "C": "airplane", "D": "pencil"},
         "answer": "C"},
}


# ===================== ENGLISH VIEW =====================
def home(request):
    if request.method == "POST":
        score = 0
        total = len(questions)

        for qno, qdata in questions.items():
            selected = request.POST.get(str(qno))
            if selected == qdata["answer"]:
                score += 1

        student_name = request.POST.get("student_name")
        student_email = request.POST.get("student_email")

        percent = round((score / total) * 100)
        status = "PASS" if percent >= 50 else "FAIL"

        ExamResult.objects.create(
            student_name=student_name,
            student_email=student_email,
            score=score,
            total=total,
            percentage=percent,
            status=status,
            subject="English"
        )

        return render(request, "result.html", {
            "score": score,
            "total": total,
            "percent": percent,
            "name": student_name,
            "email": student_email,
            "status": status
        })

    return render(request, "exam.html", {"questions": questions})


# ===================== MATHEMATICS (YOUR 30 QUESTIONS) =====================
math_questions = {
    1: {"q": "Solve: 3(2x − 1) = 5x + 7",
        "options": {"A": "7", "B": "10", "C": "4", "D": "5"},
        "answer": "C"},
    2: {"q": "Simplify: (6x² − 24) / 3x",
        "options": {"A": "2x − 8", "B": "2x − 8/x", "C": "2x − 8/3x", "D": "2x − 8/3"},
        "answer": "B"},
    3: {"q": "Solve x² − 4x − 5 = 0",
        "options": {"A": "5, −1", "B": "1, −5", "C": "2, −2", "D": "No real roots"},
        "answer": "A"},
    4: {"q": "If f(x)=2x²−3x+1, find f(3)",
        "options": {"A": "10", "B": "16", "C": "12", "D": "7"},
        "answer": "B"},
    5: {"q": "Solve system: 2x + y = 9, 3x − y = 6",
        "options": {"A": "(2,5)", "B": "(3,3)", "C": "(4,1)", "D": "(5,−1)"},
        "answer": "A"},
    6: {"q": "If sinθ = 5/13, cosθ = ?",
        "options": {"A": "12/13", "B": "5/12", "C": "8/13", "D": "9/13"},
        "answer": "A"},
    7: {"q": "sin60°cos30°",
        "options": {"A": "1/2", "B": "√3/4", "C": "√2/2", "D": "3/4"},
        "answer": "B"},
    8: {"q": "cosθ = 1/2 in 0°–360°",
        "options": {"A": "60°, 300°", "B": "30°, 150°", "C": "60°, 120°", "D": "90°, 270°"},
        "answer": "A"},
    9: {"q": "tanθ · cotθ =",
        "options": {"A": "sin²θ", "B": "1", "C": "cos²θ", "D": "secθ"},
        "answer": "B"},
    10: {"q": "sin²θ + sinθ = 0",
         "options": {"A": "0°,90°", "B": "0°,180°", "C": "0°,270°", "D": "0°,180°,360°"},
         "answer": "B"},
    11: {"q": "Triangle angles ratio 2:3:4, largest is:",
         "options": {"A": "40°", "B": "60°", "C": "80°", "D": "100°"},
         "answer": "C"},
    12: {"q": "Radius=14cm, Area=?",
         "options": {"A": "196π", "B": "28π", "C": "14π", "D": "98π"},
         "answer": "A"},
    13: {"q": "Legs 9 and 12, hypotenuse:",
         "options": {"A": "15", "B": "14", "C": "13", "D": "10"},
         "answer": "A"},
    14: {"q": "Sum of polygon exterior angles:",
         "options": {"A": "360°", "B": "180°", "C": "Depends", "D": "720°"},
         "answer": "A"},
    15: {"q": "Rectangle diagonal=25, side=7, other side:",
         "options": {"A": "20", "B": "18", "C": "24", "D": "12"},
         "answer": "C"},
    16: {"q": "Mean of 6,10,14,8,12",
         "options": {"A": "9", "B": "10", "C": "11", "D": "12"},
         "answer": "C"},
    17: {"q": "Median of 3,5,9,11,13,15,17",
         "options": {"A": "9", "B": "11", "C": "13", "D": "15"},
         "answer": "B"},
    18: {"q": "Mode of 7,9,9,10,10,10,12",
         "options": {"A": "7", "B": "9", "C": "10", "D": "12"},
         "answer": "C"},
    19: {"q": "Range of 2,9,5,14,7",
         "options": {"A": "7", "B": "9", "C": "12", "D": "14"},
         "answer": "C"},
    20: {"q": "Probability of red (6 red, 4 blue, 10 green)",
         "options": {"A": "6/20", "B": "6/10", "C": "6/15", "D": "6/12"},
         "answer": "A"},
    21: {"q": "3/4 + 5/6 =",
         "options": {"A": "19/12", "B": "41/24", "C": "23/12", "D": "11/12"},
         "answer": "A"},
    22: {"q": "25% of 360",
         "options": {"A": "60", "B": "85", "C": "90", "D": "100"},
         "answer": "C"},
    23: {"q": "Increase 80 to 100, % increase:",
         "options": {"A": "15%", "B": "20%", "C": "22.5%", "D": "25%"},
         "answer": "B"},
    24: {"q": "(4/5) ÷ (2/3)",
         "options": {"A": "6/5", "B": "10/6", "C": "12/10", "D": "5/6"},
         "answer": "A"},
    25: {"q": "Car 300km in 5hrs speed =",
         "options": {"A": "40 km/h", "B": "50 km/h", "C": "55 km/h", "D": "60 km/h"},
         "answer": "B"},
    26: {"q": "All engineers intelligent; Peter engineer → Peter is:",
         "options": {"A": "Not intelligent", "B": "Intelligent", "C": "Maybe", "D": "Unknown"},
         "answer": "B"},
    27: {"q": "5,11,23,47,__",
         "options": {"A": "94", "B": "96", "C": "99", "D": "88"},
         "answer": "A"},
    28: {"q": "Odd one out:",
         "options": {"A": "Square", "B": "Rectangle", "C": "Rhombus", "D": "Triangle"},
         "answer": "D"},
    29: {"q": "Today Wednesday, 50 days later:",
         "options": {"A": "Monday", "B": "Tuesday", "C": "Friday", "D": "Saturday"},
         "answer": "C"},
    30: {"q": "If study hard → pass. John failed.",
         "options": {"A": "He studied hard", "B": "He didn't study hard",
                     "C": "Cannot conclude", "D": "He is brilliant"},
         "answer": "B"},
}


# ===================== MATH VIEW =====================
def math_exam(request):
    if request.method == "POST":
        score = 0
        total = len(math_questions)

        for qno, qdata in math_questions.items():
            selected = request.POST.get(str(qno))
            if selected == qdata["answer"]:
                score += 1

        student_name = request.POST.get("student_name")
        student_email = request.POST.get("student_email")

        percent = round((score / total) * 100)
        status = "PASS" if percent >= 50 else "FAIL"

        ExamResult.objects.create(
            student_name=student_name,
            student_email=student_email,
            score=score,
            total=total,
            percentage=percent,
            status=status,
            subject="Mathematics"
        )

        return render(request, "result.html", {
            "score": score,
            "total": total,
            "percent": percent,
            "name": student_name,
            "email": student_email,
            "status": status
        })

    return render(request, "math_exam.html", {"math_questions": math_questions})