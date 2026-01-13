from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.utils import timezone

import random

from .models import (
    ExamResult,
    EnglishQuestion,
    MathQuestion,
    PaymentClearance,
)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponse
import csv


def verify_payment(request):
    if request.method == "POST":
        email = request.POST.get("email")
        code = request.POST.get("code")

        try:
            payment = PaymentClearance.objects.get(student_email=email, code=code)
        except PaymentClearance.DoesNotExist:
            return render(request, "payment_failed.html", {"error": "Invalid payment code"})

        if payment.is_used:
            return render(request, "payment_failed.html", {"error": "Code has already been used"})

        payment.is_used = True
        payment.used_at = timezone.now()
        payment.save()

        request.session["verified_email"] = email
        request.session["allowed_exam"] = payment.exam_type

        return redirect("select_exam")

    return render(request, "verify_payment.html")


def _user_role(user):
    if user.groups.filter(name='finance').exists():
        return 'finance'
    if user.groups.filter(name='qa').exists():
        return 'qa'
    if user.groups.filter(name='me').exists():
        return 'me'
    return 'staff'


@login_required
def clearance_dashboard(request):
    role = _user_role(request.user)
    qs = PaymentClearance.objects.all().order_by('-created_at')
    q = request.GET.get('q')
    status = request.GET.get('status')
    if q:
        qs = qs.filter(student_email__icontains=q) | qs.filter(code__icontains=q)
    if status:
        qs = qs.filter(status=status)

    paginator = Paginator(qs, 20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'clearance_dashboard.html', {'clearances': page_obj, 'role': role})


@login_required
def clearance_detail(request, pk):
    role = _user_role(request.user)
    c = PaymentClearance.objects.get(pk=pk)
    return render(request, 'clearance_detail.html', {'c': c, 'role': role})


def _require_finance(user):
    return user.is_staff and user.groups.filter(name='finance').exists()


@user_passes_test(_require_finance)
def clearance_approve(request, pk):
    c = PaymentClearance.objects.get(pk=pk)
    c.status = 'APPROVED'
    c.is_used = False
    c.save()
    # audit log
    try:
        from .models import ClearanceActionLog
        ClearanceActionLog.objects.create(user_email=request.user.email or request.user.username, action='APPROVE', payment_clearance=c)
    except Exception:
        pass
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@user_passes_test(_require_finance)
def clearance_reject(request, pk):
    c = PaymentClearance.objects.get(pk=pk)
    c.status = 'REJECTED'
    c.save()
    try:
        from .models import ClearanceActionLog
        ClearanceActionLog.objects.create(user_email=request.user.email or request.user.username, action='REJECT', payment_clearance=c)
    except Exception:
        pass
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@user_passes_test(_require_finance)
def clearance_mark_used(request, pk):
    c = PaymentClearance.objects.get(pk=pk)
    c.status = 'USED'
    c.is_used = True
    c.used_at = timezone.now()
    c.save()
    try:
        from .models import ClearanceActionLog
        ClearanceActionLog.objects.create(user_email=request.user.email or request.user.username, action='MARK_USED', payment_clearance=c)
    except Exception:
        pass
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@user_passes_test(lambda u: u.is_staff and u.groups.filter(name='qa').exists())
def clearance_flag(request, pk):
    c = PaymentClearance.objects.get(pk=pk)
    # simple flag: set status to PENDING and add note field if exists
    c.status = 'PENDING'
    c.save()
    try:
        from .models import ClearanceActionLog
        ClearanceActionLog.objects.create(user_email=request.user.email or request.user.username, action='FLAG', payment_clearance=c)
    except Exception:
        pass
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def clearance_export(request):
    if not (request.user.groups.filter(name='finance').exists() or request.user.groups.filter(name='me').exists()):
        return HttpResponse('Forbidden', status=403)
    qs = PaymentClearance.objects.all().order_by('-created_at')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payment_clearances.csv"'
    writer = csv.writer(response)
    writer.writerow(['email','code','exam_type','status','used_at','created_at'])
    for c in qs:
        writer.writerow([c.student_email, c.code, c.exam_type, c.status, c.used_at, c.created_at])
    return response


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
import random
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import EnglishQuestion, ExamResult, ExamSession
from django.core.mail import EmailMessage
from reportlab.pdfgen import canvas
from io import BytesIO

from django.conf import settings


def english_exam(request):

    # ================= PAYMENT SECURITY CHECK =================
    if "verified_email" not in request.session:
        return redirect("verify_payment")

    if request.session.get("allowed_exam") not in ["ENGLISH", "BOTH"]:
        return HttpResponse("You are not cleared for English Exam")

    # ================= PREVENT MULTIPLE ATTEMPTS =================
    if request.method == "GET" and request.GET.get("email"):
        if ExamResult.objects.filter(
            student_email=request.GET.get("email"),
            subject="English"
        ).exists():
            return render(request, "already_taken.html")

    # ================= FORM SUBMISSION =================
    if request.method == "POST":
        score = 0
        total = 35

        questions = EnglishQuestion.objects.filter(
            id__in=request.POST.getlist("question_ids")
        )

        for q in questions:
            selected = request.POST.get(str(q.id))
            if selected == q.answer:
                score += 1

        percent = round((score / total) * 100)
        status = "PASS" if percent >= 50 else "FAIL"

        name = request.POST.get("student_name")
        email = request.POST.get("student_email")

        # Save Result
        ExamResult.objects.create(
            student_name=name,
            student_email=email,
            subject="English",
            score=score,
            total=total,
            percentage=percent,
            status=status
        )

        # Mark server-side exam session completed if present
        email = request.session.get("verified_email")
        if email:
            try:
                es = ExamSession.objects.filter(student_email=email, exam_type="ENGLISH", is_completed=False).first()
                if es:
                    es.mark_completed()
            except Exception:
                pass

        # ================= PDF CERTIFICATE =================
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(200, 800, "CEPRES International University")
        p.drawString(200, 780, "Entrance Exam Certificate")
        p.drawString(100, 740, f"Student: {name}")
        p.drawString(100, 720, f"Email: {email}")
        p.drawString(100, 700, f"Subject: English")
        p.drawString(100, 680, f"Score: {score}/{total} ({percent}%)")
        p.drawString(100, 660, f"Status: {status}")
        p.showPage()
        p.save()
        buffer.seek(0)
        pdf = buffer.getvalue()

        # ================= EMAIL RESULT =================
        email_msg = EmailMessage(
            "CIU Entrance Exam Result",
            f"Dear {name},\n\nAttached is your CIU Exam Certificate.",
            "cepresiamacoe@gmail.com",
            [email, "cepresiamacoe@gmail.com"]
        )

        email_msg.attach("CIU_Result.pdf", pdf, "application/pdf")

        # Prevent Render Crash
        try:
            email_msg.send(fail_silently=True)
        except:
            pass

        # Clear persisted question ids, option orders and start time for this exam from session
        request.session.pop("english_question_ids", None)
        request.session.pop("english_q_options_order", None)
        request.session.pop("english_started_at", None)
        request.session.modified = True

        return render(request, "result.html", {
            "score": score,
            "total": total,
            "percent": percent,
            "name": name,
            "email": email,
            "status": status
        })

    # ================= LOAD RANDOM QUESTIONS =================
    # Check for timeout (server-side if stored in DB)
    email = request.session.get("verified_email")
    if email:
        try:
            sess = ExamSession.objects.filter(student_email=email, exam_type="ENGLISH", is_completed=False).first()
        except Exception:
            sess = None
        if sess:
            elapsed = (timezone.now() - sess.started_at).total_seconds()
            timeout = getattr(settings, "EXAM_TIMEOUT_SECONDS", 60 * 60)
            if elapsed > timeout:
                sess.delete()
                # also clear any session-level keys
                request.session.pop("english_question_ids", None)
                request.session.pop("english_q_options_order", None)
                request.session.pop("english_started_at", None)
                request.session.modified = True
                return render(request, "exam_expired.html", {"subject": "English"})
    # Persist 35 random question IDs and a consistent option order per question in session
    # If a server-side session exists, load from it; otherwise create one
    if email:
        sess = ExamSession.objects.filter(student_email=email, exam_type="ENGLISH", is_completed=False).first()
    else:
        sess = None

    if sess:
        selected_ids = sess.question_ids
        q_options = sess.q_options_order
        # mirror into request.session for compatibility
        request.session["english_question_ids"] = selected_ids
        request.session["english_q_options_order"] = q_options
        request.session["english_started_at"] = sess.started_at.timestamp()
        request.session.modified = True
    else:
        all_ids = list(EnglishQuestion.objects.values_list("id", flat=True))
        count = min(35, len(all_ids))
        selected_ids = random.sample(all_ids, count) if all_ids else []
        q_options = {}
        for qid in selected_ids:
            q = EnglishQuestion.objects.get(id=qid)
            letters = ["A", "B", "C", "D"]
            random.shuffle(letters)
            q_options[str(qid)] = letters
        # persist server-side if we have an email
        if email:
            ExamSession.objects.create(
                student_email=email,
                exam_type="ENGLISH",
                question_ids=selected_ids,
                q_options_order=q_options,
            )
        request.session["english_question_ids"] = selected_ids
        request.session["english_q_options_order"] = q_options
        request.session["english_started_at"] = timezone.now().timestamp()
        request.session.modified = True

    selected_ids = request.session.get("english_question_ids", [])
    questions = list(EnglishQuestion.objects.filter(id__in=selected_ids))
    id_to_q = {q.id: q for q in questions}
    selected = [id_to_q[qid] for qid in selected_ids if qid in id_to_q]

    # Apply the consistent shuffled option order saved in session / DB
    q_options_order = request.session.get("english_q_options_order", {})
    for q in selected:
        order = q_options_order.get(str(q.id), ["A", "B", "C", "D"])
        opts_map = {
            "A": q.option_a,
            "B": q.option_b,
            "C": q.option_c,
            "D": q.option_d,
        }
        q.shuffled = [(letter, opts_map[letter]) for letter in order]

    return render(request, "exam.html", {"questions": selected})


def autosave_exam(request):
    """Autosave endpoint to persist partial answers.

    Expects JSON POST with: exam_type (ENGLISH|MATH), answers (dict), name, email, question_ids (optional), q_options_order (optional), timeLeft (optional)
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    email = request.session.get("verified_email") or request.POST.get("student_email")
    if not email:
        return JsonResponse({"error": "Not authenticated/verified"}, status=403)

    try:
        data = request.body.decode("utf-8")
        import json
        payload = json.loads(data) if data else {}
    except Exception:
        payload = request.POST.dict()

    exam_type = payload.get("exam_type") or request.POST.get("exam_type")
    if not exam_type:
        return JsonResponse({"error": "exam_type required"}, status=400)

    answers = payload.get("answers") or {}
    question_ids = payload.get("question_ids")
    q_options = payload.get("q_options_order")

    sess, created = ExamSession.objects.get_or_create(
        student_email=email,
        exam_type=exam_type,
        defaults={
            "question_ids": question_ids or [],
            "q_options_order": q_options or {},
        }
    )

    # Update fields
    if question_ids:
        sess.question_ids = question_ids
    if q_options:
        sess.q_options_order = q_options
    if isinstance(answers, dict):
        # merge answers
        sess.answers.update(answers)
    sess.save()

    # mirror into request.session for compatibility
    request.session[f"{exam_type.lower()}_question_ids"] = sess.question_ids
    request.session[f"{exam_type.lower()}_q_options_order"] = sess.q_options_order
    request.session.modified = True

    return JsonResponse({"status": "ok"})


def resume_session(request, token):
    """Resume an ExamSession into the current request.session using a signed token.

    Token is signed JSON: {"session_id": <id>} and validated with TimestampSigner and RESUME_LINK_EXPIRY_SECONDS.
    """
    from django.core import signing
    try:
        expiry = getattr(settings, "RESUME_LINK_EXPIRY_SECONDS", 3600)
        data = signing.TimestampSigner().unsign(token, max_age=expiry)
        import json
        payload = json.loads(data)
        sess_id = int(payload.get("session_id"))
    except signing.BadSignature:
        return HttpResponse("Invalid resume token", status=400)
    except signing.SignatureExpired:
        return HttpResponse("Resume link expired", status=400)
    except Exception:
        return HttpResponse("Invalid token payload", status=400)

    try:
        sess = ExamSession.objects.get(pk=sess_id, is_completed=False)
    except ExamSession.DoesNotExist:
        return HttpResponse("Session not found or already completed", status=404)

    # Load into request.session
    request.session["verified_email"] = sess.student_email
    request.session["allowed_exam"] = sess.exam_type
    request.session[f"{sess.exam_type.lower()}_question_ids"] = sess.question_ids
    request.session[f"{sess.exam_type.lower()}_q_options_order"] = sess.q_options_order
    request.session[f"{sess.exam_type.lower()}_started_at"] = sess.started_at.timestamp()
    request.session.modified = True

    # Redirect to the appropriate exam page
    if sess.exam_type == "ENGLISH":
        # Log resume usage
        try:
            from .models import ResumeLog
            ResumeLog.objects.create(student_email=sess.student_email, action="USED", details=f"Resumed session {sess.id} via token")
        except Exception:
            pass
        return redirect("english_exam")
    else:
        try:
            from .models import ResumeLog
            ResumeLog.objects.create(student_email=sess.student_email, action="USED", details=f"Resumed session {sess.id} via token")
        except Exception:
            pass
        return redirect("math_exam")


@staff_member_required
def admin_active_sessions_count(request):
    """Return JSON with counts of active (not completed) ExamSession rows."""
    from .models import ExamSession
    total = ExamSession.objects.filter(is_completed=False).count()
    english = ExamSession.objects.filter(is_completed=False, exam_type='ENGLISH').count()
    math = ExamSession.objects.filter(is_completed=False, exam_type='MATH').count()
    return JsonResponse({"total": total, "english": english, "math": math})

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


# ===================== MATHEMATICS VIEW =====================
import random
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import MathQuestion, ExamResult
from django.core.mail import EmailMessage
from reportlab.pdfgen import canvas
from io import BytesIO


def math_exam(request):

    # ================= PAYMENT SECURITY CHECK =================
    if "verified_email" not in request.session:
        return redirect("verify_payment")

    if request.session.get("allowed_exam") not in ["MATH", "BOTH"]:
        return HttpResponse("You are not cleared for Math Exam")

    # ================= PREVENT MULTIPLE ATTEMPTS =================
    if request.method == "GET" and request.GET.get("email"):
        if ExamResult.objects.filter(
            student_email=request.GET.get("email"),
            subject="Math"
        ).exists():
            return render(request, "already_taken.html")

    # ================= FORM SUBMISSION =================
    if request.method == "POST":
        score = 0
        total = 30

        questions = MathQuestion.objects.filter(
            id__in=request.POST.getlist("question_ids")
        )

        for q in questions:
            selected = request.POST.get(str(q.id))
            if selected == q.answer:
                score += 1

        percent = round((score / total) * 100)
        status = "PASS" if percent >= 50 else "FAIL"

        name = request.POST.get("student_name")
        email = request.POST.get("student_email")

        # Save result
        ExamResult.objects.create(
            student_name=name,
            student_email=email,
            subject="Math",
            score=score,
            total=total,
            percentage=percent,
            status=status
        )

        # ================= PDF CERTIFICATE =================
        buffer = BytesIO()
        p = canvas.Canvas(buffer)

        p.drawString(200, 800, "CEPRES International University")
        p.drawString(200, 780, "Entrance Exam Certificate")
        p.drawString(100, 740, f"Student: {name}")
        p.drawString(100, 720, f"Email: {email}")
        p.drawString(100, 700, f"Subject: Mathematics")
        p.drawString(100, 680, f"Score: {score}/{total} ({percent}%)")
        p.drawString(100, 660, f"Status: {status}")

        p.showPage()
        p.save()
        buffer.seek(0)
        pdf = buffer.getvalue()

        # ================= EMAIL RESULT =================
        email_msg = EmailMessage(
            "CIU Entrance Exam Result",
            f"Dear {name},\n\nAttached is your CIU Exam Certificate.",
            "cepresiamacoe@gmail.com",
            [email, "cepresiamacoe@gmail.com"]
        )

        email_msg.attach("CIU_Math_Result.pdf", pdf, "application/pdf")

        try:
            email_msg.send(fail_silently=True)
        except:
            pass

        # Clear persisted question ids, option orders and start time for this exam from session
        request.session.pop("math_question_ids", None)
        request.session.pop("math_q_options_order", None)
        request.session.pop("math_started_at", None)
        request.session.modified = True

        # Mark server-side exam session completed if present
        email = request.session.get("verified_email")
        if email:
            try:
                ms = ExamSession.objects.filter(student_email=email, exam_type="MATH", is_completed=False).first()
                if ms:
                    ms.mark_completed()
            except Exception:
                pass

        return render(request, "result.html", {
            "score": score,
            "total": total,
            "percent": percent,
            "name": name,
            "email": email,
            "status": status
        })

    # ================= SELECT RANDOM QUESTIONS =================
    # Select 30 random question IDs once per exam session and store in session
    # Server-side session handling for Math (resume across devices)
    email = request.session.get("verified_email")
    if email:
        sess = ExamSession.objects.filter(student_email=email, exam_type="MATH", is_completed=False).first()
    else:
        sess = None

    if sess:
        elapsed = (timezone.now() - sess.started_at).total_seconds()
        timeout = getattr(settings, "EXAM_TIMEOUT_SECONDS", 60 * 60)
        if elapsed > timeout:
            sess.delete()
            request.session.pop("math_question_ids", None)
            request.session.pop("math_q_options_order", None)
            request.session.pop("math_started_at", None)
            request.session.modified = True
            return render(request, "exam_expired.html", {"subject": "Math"})

    if sess:
        selected_ids = sess.question_ids
        q_options = sess.q_options_order
        request.session["math_question_ids"] = selected_ids
        request.session["math_q_options_order"] = q_options
        request.session["math_started_at"] = sess.started_at.timestamp()
        request.session.modified = True
    else:
        all_ids = list(MathQuestion.objects.values_list("id", flat=True))
        count = min(30, len(all_ids))
        selected_ids = random.sample(all_ids, count) if all_ids else []
        q_options = {}
        for qid in selected_ids:
            q = MathQuestion.objects.get(id=qid)
            letters = ["A", "B", "C", "D"]
            random.shuffle(letters)
            q_options[str(qid)] = letters
        if email:
            ExamSession.objects.create(
                student_email=email,
                exam_type="MATH",
                question_ids=selected_ids,
                q_options_order=q_options,
            )
        request.session["math_question_ids"] = selected_ids
        request.session["math_q_options_order"] = q_options
        request.session["math_started_at"] = timezone.now().timestamp()
        request.session.modified = True

    selected_ids = request.session.get("math_question_ids", [])
    questions = list(MathQuestion.objects.filter(id__in=selected_ids))
    # Preserve the stored order
    id_to_q = {q.id: q for q in questions}
    selected = [id_to_q[qid] for qid in selected_ids if qid in id_to_q]

    # ================= SHUFFLE OPTIONS =================
    # Apply the consistent shuffled option order saved in session
    q_options_order = request.session.get("math_q_options_order", {})
    for q in selected:
        order = q_options_order.get(str(q.id), ["A", "B", "C", "D"])
        opts_map = {
            "A": q.option_a,
            "B": q.option_b,
            "C": q.option_c,
            "D": q.option_d,
        }
        q.shuffled = [(letter, opts_map[letter]) for letter in order]

    return render(request, "math_exam.html", {
        "questions": selected
    })
