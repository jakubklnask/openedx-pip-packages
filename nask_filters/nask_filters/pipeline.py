import logging
from openedx_filters import PipelineStep
from common.djangoapps.student.models import CourseEnrollment
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from crum import get_current_user 
from .utils import auto_enroll_user  # Importujemy wspólną logikę
log = logging.getLogger(__name__)


log = logging.getLogger(__name__)

class AutoEnrollByCorpEmail(PipelineStep):
    """
    Przy logowaniu uruchamia auto-zapisy na kursy.
    """
    def run_filter(self, user, *args, **kwargs):
        log.info(f"[NASK] Uruchomiono pipelinestep AutoEnrollByCorpEmail dla {user.username}")
        
        # Przekazanie użytkownika do głównego serwisu
        auto_enroll_user(user)
        
        return {}


class StampCoursesForDashboard(PipelineStep):
    """
    Modyfikuje dane kursu wysyłane do Dashboardu (MFE).
    Logika:
    1. Jeśli Admin/Staff -> ZAWSZE pokazuj (ustaw 'corp-auto-enrolled').
    2. Jeśli zwykły user -> Pokazuj tylko jeśli organizacja kursu == organizacja maila.
    """

    def run_filter(self, course_key, serialized_enrollment, *args, **kwargs):
        # 1. Pobieramy usera z aktualnego wątku (filtr nie przekazuje go w argumentach)
        user = get_current_user()
        
        log.info(f"[NASK] Uruchomiono pipelinestep StampCoursesForDashboardlByCorpEmail dla {user.username}")

        if not user or not user.is_authenticated:
            return {}

        # --- ADMIN PASS ---
        # Jeśli użytkownik jest członkiem obsługi (is_staff) lub superuserem -> PRZEPUŚĆ WSZYSTKO
        if user.is_staff or user.is_superuser:
            # log.info(f"[NASK] Admin Access: Stempluję kurs {course_key} dla admina {user.username}")
            serialized_enrollment['mode'] = 'corp-auto-enrolled'
            return {
                "course_key": course_key,
                "serialized_enrollment": serialized_enrollment
            }
        # ------------------

        # 2. Logika dla zwykłego użytkownika
        
        # Pobieranie organizacji kursu
        try:
            course_org = course_key.org.lower()
        except AttributeError:
            # Fallback dla starszych wersji course_key
            course_org = str(course_key).split(':')[1].split('+')[0].lower()

        # Pobieranie organizacji usera
        try:
            if not user.email or '@' not in user.email:
                return {}
            user_org_slug = user.email.split('@')[1].split('.')[0].lower()
        except Exception:
            return {}

        # 3. Porównanie i Stemplowanie
        if course_org == user_org_slug:
            # log.info(f"[NASK] MATCH! Kurs {course_key} pasuje do organizacji {user_org_slug}.")
            
            # Ustawiamy flagę uzgodnioną z Frontendem
            serialized_enrollment['mode'] = 'corp-auto-enrolled'
            
            return {
                "course_key": course_key,
                "serialized_enrollment": serialized_enrollment
            }

        return {}