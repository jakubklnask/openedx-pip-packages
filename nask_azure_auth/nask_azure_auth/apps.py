from django.apps import AppConfig
from django.conf import settings
import sys

"""EXISTING PIPELINE

common.djangoapps.third_party_auth.pipeline.parse_query_params
social_core.pipeline.social_auth.social_details
social_core.pipeline.social_auth.social_uid
social_core.pipeline.social_auth.auth_allowed
social_core.pipeline.social_auth.social_user
common.djangoapps.third_party_auth.pipeline.associate_by_email_if_login_api
common.djangoapps.third_party_auth.pipeline.associate_by_email_if_saml
common.djangoapps.third_party_auth.pipeline.associate_by_email_if_oauth
common.djangoapps.third_party_auth.pipeline.get_username
common.djangoapps.third_party_auth.pipeline.set_pipeline_timeout
common.djangoapps.third_party_auth.pipeline.ensure_user_information
social_core.pipeline.user.create_user
social_core.pipeline.social_auth.associate_user
social_core.pipeline.social_auth.load_extra_data
social_core.pipeline.user.user_details
common.djangoapps.third_party_auth.pipeline.user_details_force_sync
common.djangoapps.third_party_auth.pipeline.set_id_verification_status
common.djangoapps.third_party_auth.pipeline.set_logged_in_cookies
common.djangoapps.third_party_auth.pipeline.login_analytics
common.djangoapps.third_party_auth.pipeline.ensure_redirect_url_is_safe


""" 

class NaskAzureAuthConfig(AppConfig):
    name = "nask_azure_auth"
    verbose_name = "Nask Azure Auth Integration"

    def ready(self):
        # Ta metoda odpala się, gdy APKI SĄ JUŻ ZAŁADOWANE
        # Nie ma ryzyka "Apps aren't loaded yet"
        
        # Pobieramy to, co Django wyprodukowało jako finalny pipeline
        pipeline = list(getattr(settings, 'SOCIAL_AUTH_PIPELINE', []))
        new_step = "nask_azure_auth.auth_pipeline.process_auth_data"

        if new_step not in pipeline:
            try:
                # Szukamy kotwicy
                anchor = "social_core.pipeline.social_auth.associate_user"
                if anchor in pipeline:
                    idx = pipeline.index(anchor)
                    pipeline.insert(idx + 1, new_step)
                else:
                    pipeline.append(new_step)
                
                # Nadpisujemy ustawienie w locie (w pamięci RAM)
                settings.SOCIAL_AUTH_PIPELINE = tuple(pipeline)
                
                # Logowanie widoczne w tutor dev logs
                sys.stderr.write("!!! [NASK-AUTH] Pipeline zaktualizowany pomyslnie w ready() !!!")
            except Exception as e:
                sys.stderr.write(f"!!! [NASK-AUTH-ERROR] Blad w ready(): {e} !!!")
