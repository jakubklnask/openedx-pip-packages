import logging
from common.djangoapps.student.models import CourseEnrollment
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

log = logging.getLogger(__name__)

def auto_enroll_user(user):
    """
    Uniwersalna funkcja do zapisywania użytkowników na kursy.
    Bezpieczna do użycia zarówno przy rejestracji (signals), jak i logowaniu (pipeline).
    """
    if not user.is_active:
        return

    # Superuserów nie dotykamy (zwykle i tak mają globalny dostęp w CMS/LMS przez flagę)
    if user.is_superuser:
        return

    courses_to_enroll = []

    # 1. Ustalenie listy kursów na podstawie roli
    if user.is_staff:
        # Staff widzi wszystko
        courses_to_enroll = list(CourseOverview.objects.all())
    else:
        # Zwykły użytkownik - filtrujemy po organizacji
        if not user.email or '@' not in user.email:
            log.info(f"[NASK-ENROLL] Brak lub niepoprawny email dla: {user.username}. Pomijam.")
            return

        try:
            email_domain = user.email.split('@')[1]
            org_slug = email_domain.split('.')[0]
        except Exception as e:
            log.warning(f"[NASK-ENROLL] Błąd parsowania maila {user.email}: {e}")
            return

        courses_to_enroll = list(CourseOverview.objects.filter(org__iexact=org_slug))

    # Jeśli nie znaleziono żadnych kursów, kończymy
    if not courses_to_enroll:
        log.info(f"[NASK-ENROLL] Brak kursów do zapisania dla: {user.username}")
        return

    # 2. OPTYMALIZACJA: Pobieramy istniejące zapisy
    # Dla nowego usera z sygnału to będzie po prostu pusty set(), więc jest bezpiecznie
    existing_enrollment_ids = set(
        CourseEnrollment.objects.filter(
            user=user, 
            is_active=True
        ).values_list('course_id', flat=True)
    )

    # 3. Zapisywanie na brakujące kursy
    for course in courses_to_enroll:
        if course.id in existing_enrollment_ids:
            continue  # Pomiń, jeśli już zapisany

        try:
            log.info(f"[NASK-ENROLL] Auto-zapisywanie {user.username} na {course.id}")
            CourseEnrollment.enroll(
                user=user,
                course_key=course.id,
                mode="audit", # lub 'honor'
                check_access=True
            )
        except Exception as e:
            log.error(f"[NASK-ENROLL] Błąd zapisu usera {user.username} na {course.id}: {e}")