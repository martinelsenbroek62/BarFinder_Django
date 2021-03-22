import environ
import os
import raven
from celery.schedules import crontab

ROOT_DIR = environ.Path(__file__) - 2  # (/a/myfile.py - 2 = /)
APPS_DIR = ROOT_DIR.path('good_spot')

TEST_RUNNING = True if len(environ.sys.argv) > 1 and environ.sys.argv[1] == 'test' else False

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_SECRET_KEY=(str, 'sy*l$jo8e0%!8w&b#zb*#%_1d5%-%ob&7bvlb86%td+s^!*_(9'),
    DJANGO_ADMINS=(list, []),
    DJANGO_ALLOWED_HOSTS=(list, []),
    DJANGO_STATIC_ROOT=(str, str(APPS_DIR('staticfiles'))),
    DJANGO_MEDIA_ROOT=(str, str(APPS_DIR('media'))),
    DJANGO_DATABASE_URL=(str, 'postgis:///good_spot'),
    DJANGO_EMAIL_URL=(environ.Env.email_url_config, 'consolemail://'),
    DJANGO_DEFAULT_FROM_EMAIL=(str, 'admin@example.com'),
    DJANGO_EMAIL_BACKEND=(str, 'django.core.mail.backends.smtp.EmailBackend'),
    DJANGO_SERVER_EMAIL=(str, 'root@localhost.com'),

    DJANGO_CELERY_BROKER_URL=(str, 'amqp://guest:guest@localhost:5672//'),
    DJANGO_CELERY_ALWAYS_EAGER=(bool, False),

    DJANGO_USE_DEBUG_TOOLBAR=(bool, False),
    DJANGO_USE_DEBUG_PANEL=(bool, False),
    DJANGO_TEST_RUN=(bool, False),

    DJANGO_HEALTH_CHECK_BODY=(str, 'Success'),
    DJANGO_USE_SILK=(bool, False),

    DJANGO_GOOGLE_PLACES_API_KEY=(str, ''),
    DJANGO_MAPS_PLACES_API_KEY=(str, ''),

    DJANGO_SEOPROXY_APIUSERID=(int, None),
    DJANGO_SEOPROXY_APIKEY=(str, ''),

    DJANGO_AWS_S3_USE_ROLES=(bool, False),
    DJANGO_USE_AWS=(bool, False),
    DJANGO_AWS_ACCESS_KEY_ID=(str, ''),
    DJANGO_AWS_SECRET_ACCESS_KEY=(str, ''),
    DJANGO_AWS_STORAGE_BUCKET_NAME=(str, ''),
    DJANGO_AWS_S3_REGION_NAME=(str, ''),
    DJANGO_AWS_S3_CUSTOM_DOMAIN=(str, ''),
    DJANGO_MEDIA_DOMAIN=(str, ''),

    DJANGO_NOTIFIER_SECRET=(str, "secret"),
)

environ.Env.read_env()

DEBUG = env.bool('DJANGO_DEBUG')

SECRET_KEY = env('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')

ADMINS = tuple([tuple(admins.split(':')) for admins in env.list('DJANGO_ADMINS')])

MANAGERS = ADMINS

TIME_ZONE = 'UTC'

LANGUAGE_CODE = 'en-us'

gettext = lambda s: s
LANGUAGES = (
    ('en', gettext('English')),
    ('fr', gettext('French')),
    ('ru', gettext('Russian')),
    ('uk', gettext('Ukrainian')),
)
MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'
MODELTRANSLATION_PREPOPULATE_LANGUAGE = 'en'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATABASES = {
    'default': env.db('DJANGO_DATABASE_URL')
}

DJANGO_APPS = (
    'django.contrib.auth',
    'polymorphic',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.gis',
    'django.forms',
    'django.contrib.postgres',
)

THIRD_PARTY_APPS = (
    'django_extensions',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'constance',
    'constance.backends.database',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger',
    'rest_auth',
    'rest_auth.registration',
    'phonenumber_field',
    'prettyjson',
    'adminsortable2',
    'cities_light',
    'djangobower',
    'storages',
    'django_filters',
    'ckeditor',
    'sorl.thumbnail',
    'schedule',
)

LOCAL_APPS = (
    'good_spot.common.apps.CommonConfig',
    'good_spot.users.apps.UsersConfig',
    'good_spot.places.apps.PlacesConfig',
    'good_spot.proxy.apps.ProxyConfig',
    'good_spot.events.apps.EventsConfig',
    'good_spot.images.apps.ImagesConfig',
    'good_spot.report.apps.ReportConfig',
    'good_spot.filter.apps.FilterConfig',
    'good_spot.populartimes.apps.PopulartimesConfig',
    'good_spot.place_editor.apps.PlaceEditorConfig',
    'good_spot.pages.apps.PagesConfig',
)

BOWER_INSTALLED_APPS = (
    'jquery',
    'jquery-ui',
    'bootstrap'
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTH_USER_MODEL = 'users.User'
ADMIN_URL = r'^admin/'

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'good_spot.common.middleware.AdminLocaleMiddleware',
]

EMAIL_URL = env.email_url('DJANGO_EMAIL_URL')
EMAIL_BACKEND = EMAIL_URL['EMAIL_BACKEND']
EMAIL_HOST = EMAIL_URL.get('EMAIL_HOST', '')
if EMAIL_URL.get('EMAIL_HOST_PASSWORD', '') == 'special':
    EMAIL_HOST_PASSWORD = env('DJANGO_EMAIL_HOST_PASSWORD_SPECIAL')
else:
    EMAIL_HOST_PASSWORD = EMAIL_URL.get('EMAIL_HOST_PASSWORD', '')
EMAIL_HOST_USER = EMAIL_URL.get('EMAIL_HOST_USER', '')
EMAIL_PORT = EMAIL_URL.get('EMAIL_PORT', '')
EMAIL_USE_SSL = 'EMAIL_USE_SSL' in EMAIL_URL
EMAIL_USE_TLS = 'EMAIL_USE_TLS' in EMAIL_URL
EMAIL_FILE_PATH = EMAIL_URL.get('EMAIL_FILE_PATH', '')

DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL')

SERVER_EMAIL = env('DJANGO_SERVER_EMAIL')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            'debug': DEBUG,
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',

            ],
        },
    },
]
FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

STATIC_URL = '/static/'
STATIC_ROOT = env('DJANGO_STATIC_ROOT')

MEDIA_URL = '/media/'
MEDIA_ROOT = env('DJANGO_MEDIA_ROOT')

STATICFILES_DIRS = (
    str(APPS_DIR.path('static')),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
)

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

# celery settings
BROKER_URL = env('DJANGO_CELERY_BROKER_URL')
CELERY_ALWAYS_EAGER = env.bool('DJANGO_CELERY_ALWAYS_EAGER')
CELERYBEAT_SCHEDULE = {
    'run-fill-place-async': {
        'task': 'good_spot.places.tasks.run_fill_place_async',
        'schedule': crontab(minute=15, hour=12),
    },
    # 'run-periodic-update': {
    #     'task': 'good_spot.places.tasks.run_periodic_updates',
    #     'schedule': crontab(hour='*', minute=1),
    # },
    # # 'run-periodic-update': {
    # #     'task': 'good_spot.places.tasks.run_periodic_updates',
    # #     'schedule': crontab(hour='*', minute=1),
    # # },
    'run-hourly-update': {
        'task': 'good_spot.places.tasks.run_hourly_updates',
        'schedule': crontab(hour='*', minute=1),
    },
    'run-periodic-cleaning-expired-populartimes': {
        'task': 'good_spot.places.tasks.run_periodic_cleaning_expired_populartimes',
        'schedule': crontab(hour='*', minute=0)
    },
    'run-periodic-reset-counter': {
        'task': 'good_spot.proxy.tasks.run_periodic_reset_counter',
        'schedule': crontab(hour='*', minute=0)
    }
}
CELERY_IMPORTS = (
    'good_spot.common.tasks',
    'good_spot.places.tasks',
    'good_spot.proxy.tasks',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/email_confirmed/'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/email_confirmed/'

SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_QUERY_EMAIL = True
OLD_PASSWORD_FIELD_ENABLED = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
            'level': 'ERROR',
            'filters': ['require_debug_false'],
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARN',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'propagate': True,
            'level': 'ERROR',
        },
    }
}

if os.environ.get('SENTRY_DSN'):
    INSTALLED_APPS += ('raven.contrib.django.raven_compat',)
    RAVEN_CONFIG = {
        'dsn': env('SENTRY_DSN'),
        'release': raven.fetch_git_sha(str(ROOT_DIR)),
    }

USE_DEBUG_TOOLBAR = env.bool('DJANGO_USE_DEBUG_TOOLBAR') if not TEST_RUNNING else False
USE_DEBUG_PANEL = env.bool('DJANGO_USE_DEBUG_PANEL') if not TEST_RUNNING else False
if USE_DEBUG_TOOLBAR:
    middleware = 'debug_panel.middleware.DebugPanelMiddleware' if USE_DEBUG_PANEL else 'debug_toolbar.middleware.DebugToolbarMiddleware'  # noqa
    MIDDLEWARE += [
        middleware
    ]
    INSTALLED_APPS += (
        'debug_toolbar',
        'debug_panel',
    )
    DEBUG_TOOLBAR_CONFIG = {
        'DISABLE_PANELS': [
            'debug_toolbar.panels.redirects.RedirectsPanel',
        ],
        'SHOW_TEMPLATE_CONTEXT': True,
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
    }

    DEBUG_TOOLBAR_PATCH_SETTINGS = False

    # http://django-debug-toolbar.readthedocs.org/en/latest/installation.html
    INTERNAL_IPS = ('127.0.0.1', '0.0.0.0', '10.0.2.2')

if env.bool('DJANGO_TEST_RUN'):
    pass

HEALTH_CHECK_BODY = env('DJANGO_HEALTH_CHECK_BODY')

# Silk config
USE_SILK = env('DJANGO_USE_SILK')
if USE_SILK:
    INSTALLED_APPS += (
        'silk',
    )
    MIDDLEWARE += [
        'silk.middleware.SilkyMiddleware',
    ]
    SILKY_AUTHENTICATION = True  # User must login
    SILKY_AUTHORISATION = True  # User must have permissions
    SILKY_PERMISSIONS = lambda user: user.is_superuser

# Django constance config
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_CONFIG = {
    'EXTRAPOLATE_FOR_NUM_HOURS': (3, 'Extrapolate live time for specified number of hours.'),
    'LIVE_IS_ACTUAL_FOR_NUM_HOURS': (12, 'Number of hours when Live is actual.'),
    'MAX_REQUESTS_PER_HOUR': (10, 'The recommended continued rate per hour per IP.'),
    'DELAY_BETWEEN_PROXY_REQUESTS_IN_MINUTES': (4, 'Recommended delay between requests using proxy '
                                                   '(provide in minutes). \nShould be at least 4, because '
                                                   '`seo-proxies.com` recommends max 15 requests per hour per one IP.'),
    'MIN_IMAGE_SIZE': (600, 'The minimum size of the user image.'),
    'CONTACT_EMAIL': ('', 'Reports from users are sending to this email.'),
    'UPDATE_PLACES_HOURLY': (True, 'Do you want to run hourly updates of active places? (Proxies will be used.)'),
    'ANDROID_CURRENT_VERSION':('','android app current version'),
    'IOS_CURRENT_VERSION':('','ios app current version'),
}

GOOGLE_PLACES_API_KEY = env('DJANGO_GOOGLE_PLACES_API_KEY')
GOOGLE_MAPS_API_KEY = env('DJANGO_MAPS_PLACES_API_KEY')

# DRF config
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
}
if not DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
        'rest_framework.renderers.JSONRenderer',
    )

CITIES_LIGHT_TRANSLATION_LANGUAGES = ['fr', 'en', 'es', 'de', 'ru', 'ua']
CITIES_LIGHT_TRANSLATION_SOURCES = [
    'http://download.geonames.org/export/dump/alternatenames/UA.zip',
    'http://download.geonames.org/export/dump/alternatenames/FR.zip',
    'http://download.geonames.org/export/dump/alternatenames/RU.zip'
]

SEOPROXY_APIUSERID = env('DJANGO_SEOPROXY_APIUSERID')
SEOPROXY_APIKEY = env('DJANGO_SEOPROXY_APIKEY')

BOWER_COMPONENTS_ROOT = str(APPS_DIR.path('static'))


USE_AWS = env('DJANGO_USE_AWS')
if USE_AWS:
    AWS_S3_USE_ROLES = env('DJANGO_AWS_S3_USE_ROLES')
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = env('DJANGO_AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('DJANGO_AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('DJANGO_AWS_STORAGE_BUCKET_NAME')
    AWS_S3_CUSTOM_DOMAIN = env("DJANGO_AWS_S3_CUSTOM_DOMAIN")
    AWS_S3_REGION_NAME = env('DJANGO_AWS_S3_REGION_NAME')
    MEDIA_DOMAIN = env('DJANGO_MEDIA_DOMAIN')
    MEDIA_URL = MEDIA_DOMAIN + '/'
else:
    MEDIA_URL = '/media/'

NOTIFIER_SECRET = env("DJANGO_NOTIFIER_SECRET")

# 2.5MB - 2621440
# 5MB - 5242880
# 10MB - 10485760
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880

REST_AUTH_SERIALIZERS = {
    'TOKEN_SERIALIZER': 'good_spot.users.serializers.TokenSerializer',
    'PASSWORD_CHANGE_SERIALIZER': 'good_spot.users.serializers.CustomPasswordChangeSerializer',
    'PASSWORD_RESET_SERIALIZER': 'good_spot.users.serializers.PasswordResetSerializerCustom',
    'LOGIN_SERIALIZER': 'good_spot.users.serializers.LoginSerializerCustom'
}
REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'good_spot.users.serializers.RegisterSerializer'
}

# SWAGGER SETTIGNS
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
        }
    },
    'SHOW_REQUEST_HEADERS': True,
    'APIS_SORTER': 'alpha'
}

LOCALE_PATHS = [
    str(ROOT_DIR.path('locale')),
]

LOGIN_URL = '/admin/login/'
