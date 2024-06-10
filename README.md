# Platforma Charytatywna

## Opis
Platforma Charytatywna to aplikacja internetowa opracowana przy użyciu frameworka Django do zarządzania darowiznami i wydarzeniami charytatywnymi.

## Funkcjonalność

### Strona Główna
Widok strony głównej serwisu, który wyświetla główne statystyki oraz listę instytucji. Zlicza łączną liczbę worków z darowizn oraz liczbę wspieranych instytucji. Umożliwia paginację dla listy instytucji w trzech kategoriach: fundacje, NGO i zbiórki lokalne.

### Dodanie Darowizny
Widok formularza dodawania darowizny, umożliwiający zalogowanemu użytkownikowi przekazanie darowizny. Sprawdza poprawność wprowadzonych danych i zapisuje darowiznę do bazy danych.

### Potwierdzenie Formularza
Widok potwierdzenia formularza dodawania darowizny, wyświetlany po pomyślnym dodaniu darowizny.

### Logowanie
Widok logowania użytkownika. Umożliwia użytkownikom logowanie się na swoje konto. Weryfikuje dane logowania i autoryzuje użytkownika.

### Rejestracja
Widok rejestracji nowego użytkownika. Umożliwia tworzenie nowych kont użytkowników. Sprawdza poprawność danych rejestracyjnych i zapisuje użytkownika do bazy danych.

### Aktywacja Konta
Widok aktywacji konta użytkownika za pomocą emaila weryfikacyjnego. Weryfikuje token i aktywuje konto użytkownika.

### Wylogowanie
Widok wylogowania użytkownika. Wylogowuje użytkownika z sesji.

### Profil Użytkownika
Widok profilu użytkownika, wyświetlający dane użytkownika oraz listę jego darowizn. Umożliwia filtrowanie i wyszukiwanie darowizn.

### Edycja Profilu
Widok edycji profilu użytkownika, umożliwiający aktualizację danych osobowych.

### Zmiana Hasła
Widok zmiany hasła użytkownika, umożliwiający aktualizację hasła.

### Resetowanie Hasła
Widok żądania resetowania hasła, umożliwiający użytkownikowi zainicjowanie procesu resetowania hasła. Wysyła email z linkiem do resetowania hasła.

### Potwierdzenie Resetu Hasła
Widok potwierdzenia resetu hasła, umożliwiający użytkownikowi ustawienie nowego hasła. Weryfikuje token resetu hasła i zapisuje nowe hasło użytkownika.

### Kontakt
Widok kontaktowy, umożliwiający użytkownikom wysyłanie wiadomości kontaktowych do administratorów serwisu.

### Polityka Prywatności
Widok polityki prywatności, wyświetlający zasady ochrony danych osobowych.

### Warunki Korzystania z Usługi
Widok warunków korzystania z usługi, wyświetlający zasady korzystania z serwisu.

### Zgłaszanie Problemów
Widok zgłaszania problemów, umożliwiający użytkownikom zgłaszanie problemów z serwisem.

## Instalacja
Wykonaj te kroki, aby zainstalować i uruchomić projekt na lokalnym komputerze.

### Klonowanie repozytorium
Najpierw sklonuj repozytorium:

git clone https://github.com/OleksandrKiris/Oddam-w-dobre-r-ce.git
cd charity_platform

#Tworzenie i aktywacja wirtualnego środowiska

# Utwórz wirtualne środowisko i aktywuj je:

python -m venv env
source env/bin/activate  # Dla Windows użyj `env\Scripts\activate`

# Instalacja zależności

## Зainstaluj wszystkie niezbędne zależności:

pip install -r requirements.txt

# Konfiguracja zmiennych środowiskowych

## Utwórz plik .env в katalogu głównym projektu i dodaj do niego następujące linie, вypełniając je swoimi wartościami:

SECRET_KEY=your_secret_key
DEBUG=True
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port
EMAIL_BACKEND=your_email_backend
EMAIL_HOST=your_email_host
EMAIL_PORT=your_email_port
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email_host_user
EMAIL_HOST_PASSWORD=your_email_host_password
DEFAULT_FROM_EMAIL=your_default_from_email

# Zastosowanie migracji bazy danych

## Zastosuj migracje, aby utworzyć odpowiednie tabele в bazie danych:

python manage.py migrate

# Uruchomienie serwera deweloperskiego

## Uruchom serwer deweloperski:

python manage.py runserver

# Użytkowanie

##Otwórz przeglądarkę internetową i przejdź do http://127.0.0.1:8000/, aby uzyskać dostęp do aplikacji. Aby uzyskać dostęp do panelu administratora, użyj http://127.0.0.1:8000/admin/.

# Kontakt
Автор: OLEKSANDR Kiris
Email: oleksandr.kiris@icloud.com