#!/usr/bin/env python
import sys
from django.conf import settings


settings.configure(
    DATABASES={
        'default': {'ENGINE': 'django.db.backends.sqlite3'}
    },
    INSTALLED_APPS=[
        'htpayway',
    ],
    MIDDLEWARE_CLASSES=[],
)


if __name__ == '__main__':
    from django.test.simple import run_tests
    failures = run_tests(['htpayway'], verbosity=1)
    sys.exit(failures)
