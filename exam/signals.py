from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from .models import PaymentClearance, ClearanceLog
from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver


def send_clearance(instance):
    """
    Reusable email sending logic
    Used for: auto-send + resend button
    """

    html_content = render_to_string("emails/clearance_email.html", {
        "email": instance.student_email,
        "exam_type": instance.exam_type,
        "code": instance.code,
    })

    email = EmailMessage(
        subject="CIU Entrance Exam Clearance",
        body=html_content,
        from_email="CEPRES International University <cepresiamacoe@gmail.com>",
        to=[instance.student_email],
    )

    email.content_subtype = "html"

    try:
        email.send(fail_silently=False)

        instance.email_sent = True
        instance.last_email_at = timezone.now()
        instance.save(update_fields=["email_sent", "last_email_at"])

        ClearanceLog.objects.create(
            student_email=instance.student_email,
            action="EMAIL_SENT",
            details=f"Clearance email successfully sent. Code: {instance.code}",
        )

    except Exception as e:
        instance.email_sent = False
        instance.save(update_fields=["email_sent"])

        ClearanceLog.objects.create(
            student_email=instance.student_email,
            action="EMAIL_FAILED",
            details=str(e),
        )


# ================= AUTO SEND ON CREATE =================
@receiver(post_save, sender=PaymentClearance)
def auto_email_clearance(sender, instance, created, **kwargs):
    if created:  # only when first issued
        ClearanceLog.objects.create(
            student_email=instance.student_email,
            action="CREATED",
            details=f"Clearance created for {instance.exam_type}",
        )

        send_clearance(instance)


# ================= CLEAR EXAM SESSION ON LOGOUT =================
@receiver(user_logged_out)
def clear_exam_session_on_logout(sender, request, user, **kwargs):
    if not request:
        return
    # Remove any exam-related session keys to prevent reuse across logins
    keys = [
        "english_question_ids",
        "english_q_options_order",
        "english_started_at",
        "math_question_ids",
        "math_q_options_order",
        "math_started_at",
    ]
    for k in keys:
        try:
            request.session.pop(k, None)
        except Exception:
            pass
    request.session.modified = True
    # Also remove any server-side ExamSession rows for this email
    try:
        from .models import ExamSession
        if user and hasattr(user, 'email') and user.email:
            ExamSession.objects.filter(student_email=user.email, is_completed=False).delete()
        else:
            # fallback: use session verified_email
            email = request.session.get('verified_email')
            if email:
                ExamSession.objects.filter(student_email=email, is_completed=False).delete()
    except Exception:
        pass
