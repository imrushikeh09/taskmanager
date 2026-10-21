import os

# Dynamically route settings based on DJANGO_ENV
env = os.getenv("DJANGO_ENV", "development").lower()

if env == "production":
    from .production import *
elif env in ("testing", "test"):
    from .testing import *
else:
    from .development import *
