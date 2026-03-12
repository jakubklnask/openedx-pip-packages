# nask_filters/signals.py
import logging
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from .utils import auto_enroll_user  # Importujemy wspólną logikę

log = logging.getLogger(__name__)
User = get_user_model()

@receiver(post_save, sender=User)
def auto_enroll_on_creation(sender, instance, created, **kwargs):
    """
    Uruchamia auto-zapis przy pierwszej rejestracji nowego użytkownika.
    """
    log.info(f"[NASK] Uruchomiono Django signal AutoEnrolStampCoursesForDashboardlByCorpEmail")
    if not created or kwargs.get('raw'):
        return

    if instance.username in ['ecommerce_worker', 'lms_worker', 'cms_worker']:
        return

    from django.db import connection
    if 'course_overviews_courseoverview' not in connection.introspection.table_names():
        return

    log.info(f"[NASK-SIGNAL] Nowy użytkownik {instance.username}. Uruchamiam auto_enroll_user.")
    
    # Przekazanie użytkownika do głównego serwisu
    auto_enroll_user(instance)