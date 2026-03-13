
from tutor import hooks

# Dodaj tutaj wszystkie originy, które mają być dopuszczone
ORIGINS = [
    "https://edu.technologie.sp.nask.pl",
    "https://apps.edu.technologie.sp.nask.pl",
    "https://studio.edu.technologie.sp.nask.pl",
]

def _patch_block(origins):
    lines = ["# --- tutor-mycors: CORS/CSRF ---"]

    "SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')",
        
    # Stop Django from issuing its own redirects (avoids the 308 loop)
    "SECURE_SSL_REDIRECT = False",
        
    # Ensure cookies are sent over HTTPS
    "SESSION_COOKIE_SECURE = True",
    "CSRF_COOKIE_SECURE = True",    
    # Ensure variables exist
    lines.append("if 'CORS_ORIGIN_WHITELIST' not in locals(): CORS_ORIGIN_WHITELIST = []")
    lines.append("if 'CSRF_TRUSTED_ORIGINS' not in locals(): CSRF_TRUSTED_ORIGINS = []")
    
    for o in origins:
        # Force add HTTPS version
        lines.append(f'if "{o}" not in CORS_ORIGIN_WHITELIST: CORS_ORIGIN_WHITELIST.append("{o}")')
        lines.append(f'if "{o}" not in CSRF_TRUSTED_ORIGINS: CSRF_TRUSTED_ORIGINS.append("{o}")')
    
    lines.append("CORS_ALLOW_CREDENTIALS = True")
    return "\n".join(lines)

# Patch dla LMS (production)
hooks.Filters.ENV_PATCHES.add_item((
    "openedx-lms-production-settings",
    _patch_block(ORIGINS),
))

# Patch dla CMS/Studio (production)
hooks.Filters.ENV_PATCHES.add_item((
    "openedx-cms-production-settings",
    _patch_block(ORIGINS),
))
