"""Order signals: queue lifecycle emails (sent async by Celery).

Complements apps.notifications.signals, which creates in-app notifications.
Emails are dispatched through transaction.on_commit so a worker never reads
an order that is still rolling back.
"""

from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.orders.models import Order


@receiver(pre_save, sender=Order)
def _stash_status_for_emails(sender, instance, **kwargs):
    """Remember the persisted status so post_save can detect real changes."""
    if instance.pk:
        instance._email_old_status = (
            sender.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
        )
    else:
        instance._email_old_status = None


@receiver(post_save, sender=Order)
def _queue_order_emails(sender, instance, created, **kwargs):
    # Local import: tasks imports models, models import happens early.
    from apps.orders import tasks

    order_id = str(instance.pk)
    if created:
        transaction.on_commit(lambda: tasks.send_order_confirmation_email.delay(order_id))
        owner_id = instance.restaurant.owner_id if instance.restaurant_id else None
        if owner_id and owner_id != instance.user_id:
            transaction.on_commit(lambda: tasks.send_new_order_email.delay(order_id))
        return
    old_status = getattr(instance, "_email_old_status", None)
    if old_status and old_status != instance.status:
        new_status = instance.status
        transaction.on_commit(lambda: tasks.send_order_status_email.delay(order_id, new_status))
