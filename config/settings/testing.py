from .development import *

DEBUG = False

# Fast MD5 hasher to boost test suite execution speed
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Eager Celery execution during automated unit tests
CELERY_TASK_ALWAYS_EAGER = True
