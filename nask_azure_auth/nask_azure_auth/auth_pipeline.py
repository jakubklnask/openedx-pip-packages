import logging
import sys

log = logging.getLogger(__name__)

def process_auth_data(backend, response, details, user=None, *args, **kwargs):
    """
    Krok potoku logowania wywoływany PO stworzeniu/pobraniu użytkownika.
    """
    if not user:
        sys.stderr.write("!!! [NASK-AUTH] Brak obiektu user - krok jest za wcześnie w pipeline! !!!\\n")
        return None

    email = details.get('email')
    sys.stderr.write(f"!!! [NASK-AUTH] Przetwarzanie uprawnień dla: {email} (User ID: {user.id}) !!!\\n")

    # TESTOWY WARUNEK: Nadajemy Staffa dla Twojego maila
    # W przyszłości tutaj sprawdzisz: if "TWOJE_ID_GRUPY" in response.get('groups', [])
    if email == 'sagrodat333@gmail.com':
        if not user.is_staff:
            user.is_staff = True
            user.save()
            sys.stderr.write(f"!!! [NASK-AUTH] Użytkownik {email} otrzymał uprawnienia STAFF !!!\\n")
        else:
            sys.stderr.write(f"!!! [NASK-AUTH] Użytkownik {email} już posiada STAFF !!!\\n")

    return None