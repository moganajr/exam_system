from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from .models import PaymentClearance, ClearanceLog


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
