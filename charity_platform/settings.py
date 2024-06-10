import os
from pathlib import Path
from decouple import config

# Ustalanie ścieżek wewnątrz projektu, np. BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Ustawienia szybkiego startu do rozwoju - nieodpowiednie do produkcji
# Zobacz https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# OSTRZEŻENIE BEZPIECZEŃSTWA: zachowaj klucz sekretu używany w produkcji w tajemnicy!
SECRET_KEY = config('SECRET_KEY')

# OSTRZEŻENIE BEZPIECZEŃSTWA: nie uruchamiaj debugowania w produkcji!
DEBUG = config('DEBUG', default=False, cast=bool)

# Hosty dozwolone do obsługi aplikacji
ALLOWED_HOSTS = []

# Definicja aplikacji

INSTALLED_APPS = [
    'django.contrib.admin',  # Aplikacja panelu administracyjnego
    'django.contrib.auth',  # Aplikacja uwierzytelniania użytkowników
    'django.contrib.contenttypes',  # Aplikacja typów treści
    'django.contrib.sessions',  # Aplikacja sesji
    'django.contrib.messages',  # Aplikacja wiadomości
    'django.contrib.staticfiles',  # Aplikacja plików statycznych
    'donations',  # Własna aplikacja darowizn
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Middleware zabezpieczeń
    'django.contrib.sessions.middleware.SessionMiddleware',  # Middleware sesji
    'django.middleware.common.CommonMiddleware',  # Middleware wspólnych operacji
    'django.middleware.csrf.CsrfViewMiddleware',  # Middleware ochrony przed CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Middleware uwierzytelniania
    'django.contrib.messages.middleware.MessageMiddleware',  # Middleware wiadomości
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Middleware ochrony przed clickjackingiem
]

ROOT_URLCONF = 'charity_platform.urls'  # Główna konfiguracja URLi

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',  # Backend szablonów Django
        'DIRS': [BASE_DIR / 'templates'],  # Globalny katalog szablonów (jeśli potrzebny)
        'APP_DIRS': True,  # Wyszukiwanie szablonów w katalogach aplikacji
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',  # Procesor kontekstu debugowania
                'django.template.context_processors.request',  # Procesor kontekstu żądania
                'django.contrib.auth.context_processors.auth',  # Procesor kontekstu uwierzytelniania
                'django.contrib.messages.context_processors.messages',  # Procesor kontekstu wiadomości
            ],
        },
    },
]

WSGI_APPLICATION = 'charity_platform.wsgi.application'  # Aplikacja WSGI

# Baza danych
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # Silnik bazy danych PostgreSQL
        'NAME': config('DB_NAME'),  # Nazwa bazy danych
        'USER': config('DB_USER'),  # Użytkownik bazy danych
        'PASSWORD': config('DB_PASSWORD'),  # Hasło użytkownika bazy danych
        'HOST': config('DB_HOST'),  # Host bazy danych
        'PORT': config('DB_PORT', default=''),  # Port bazy danych (domyślnie pusty)
    }
}

# Walidacja haseł
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',  # Walidator podobieństwa atrybutów użytkownika
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',  # Walidator minimalnej długości hasła
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',  # Walidator popularnych haseł
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',  # Walidator numerycznych haseł
    },
]

# Międzynarodowość
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'pl'  # Kod języka

TIME_ZONE = 'Europe/Warsaw'  # Strefa czasowa

USE_I18N = True  # Użycie międzynarodowości

USE_TZ = True  # Użycie stref czasowych

# Pliki statyczne (CSS, JavaScript, Obrazy)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = '/static/'  # URL dla plików statycznych

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'donations/static'),  # Katalog plików statycznych aplikacji donations
]

STATIC_ROOT = BASE_DIR / 'staticfiles'  # Główny katalog dla plików statycznych

# Domyślny typ pola klucza głównego
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'  # Domyślne pole klucza głównego

# Ustawienia poczty email
EMAIL_BACKEND = config('EMAIL_BACKEND')  # Backend poczty email
EMAIL_HOST = config('EMAIL_HOST')  # Host poczty email
EMAIL_PORT = config('EMAIL_PORT', cast=int)  # Port poczty email
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)  # Użycie TLS dla poczty email
EMAIL_HOST_USER = config('EMAIL_HOST_USER')  # Użytkownik poczty email
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')  # Hasło użytkownika poczty email
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')  # Domyślny adres nadawcy poczty email
