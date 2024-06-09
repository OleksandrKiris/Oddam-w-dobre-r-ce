import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from django.core.exceptions import ValidationError
import re


class Category(models.Model):
    """
    Model reprezentujący kategorię darowizny.

    Atrybuty:
        name (str): Nazwa kategorii. Unikalna, maksymalna długość 255 znaków.
    """
    name = models.CharField(max_length=255, unique=True,
                            verbose_name="Nazwa")  # "Pole dla nazwy kategorii, maksymalna długość 255 znaków, musi być unikalna"

    class Meta:
        verbose_name = "Kategoria"  # "Pojedyncza kategoria"
        verbose_name_plural = "Kategorie"  # "Wiele kategorii"
        ordering = ['name']  # "Sortowanie kategorii według nazwy"

    def __str__(self):
        return self.name  # "Zwraca nazwę kategorii jako reprezentację obiektu"


class Institution(models.Model):
    """
    Model reprezentujący instytucję.

    Atrybuty:
        name (str): Nazwa instytucji.
        description (str): Opis instytucji.
        type (str): Typ instytucji (fundacja, NGO, zbiórka lokalna).
        categories (QuerySet): Kategorie powiązane z instytucją.
        created_at (datetime): Data utworzenia instytucji.
    """
    FOUNDATION = 'fundacja'
    NGO = 'organizacja pozarządowa'
    LOCAL_COLLECTION = 'zbiórka lokalna'

    TYPE_CHOICES = [
        (FOUNDATION, 'Fundacja'),  # "Opcja typu: Fundacja"
        (NGO, 'Organizacja pozarządowa'),  # "Opcja typu: Organizacja pozarządowa"
        (LOCAL_COLLECTION, 'Zbiórka lokalna'),  # "Opcja typu: Zbiórka lokalna"
    ]

    name = models.CharField(max_length=255, unique=True,
                            verbose_name="Nazwa")  # "Pole dla nazwy instytucji, maksymalna długość 255 znaków, musi być unikalna"
    description = models.TextField(verbose_name="Opis")  # "Pole dla opisu instytucji"
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default=FOUNDATION,
                            verbose_name="Typ")  # "Pole wyboru typu instytucji"
    categories = models.ManyToManyField(Category, verbose_name="Kategorie")  # "Pole wielu do wielu dla kategorii"
    created_at = models.DateTimeField(auto_now_add=True)  # "Pole dla daty utworzenia instytucji"

    class Meta:
        verbose_name = "Instytucja"  # "Pojedyncza instytucja"
        verbose_name_plural = "Instytucje"  # "Wiele instytucji"
        ordering = ['name']  # "Sortowanie instytucji według nazwy"

    def __str__(self):
        return self.name  # "Zwraca nazwę instytucji jako reprezentację obiektu"


class Donation(models.Model):
    """
    Model reprezentujący darowiznę.

    Atrybuty:
        quantity (int): Ilość worków.
        categories (QuerySet): Kategorie powiązane z darowizną.
        institution (Institution): Instytucja powiązana z darowizną.
        address (str): Adres darczyńcy.
        phone_number (str): Numer telefonu darczyńcy.
        city (str): Miasto darczyńcy.
        zip_code (str): Kod pocztowy darczyńcy.
        pick_up_date (date): Data odbioru darowizny.
        pick_up_time (time): Czas odbioru darowizny.
        pick_up_comment (str): Komentarz do odbioru.
        user (User): Użytkownik powiązany z darowizną.
        is_taken_by_user (bool): Czy darowizna została odebrana przez użytkownika.
        is_taken_by_courier (bool): Czy darowizna została odebrana przez kuriera.
        courier (User): Kurier powiązany z darowizną.
        status (str): Status darowizny.
        created_at (datetime): Data utworzenia darowizny.
        updated_at (datetime): Data ostatniej aktualizacji darowizny.
    """
    STATUS_CHOICES = [
        ('pending', 'Oczekujące'),  # "Opcja statusu: Oczekujące"
        ('in_progress', 'W trakcie realizacji'),  # "Opcja statusu: W trakcie realizacji"
        ('completed', 'Zrealizowane'),  # "Opcja statusu: Zrealizowane"
    ]

    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)],
                                           verbose_name="Ilość worków")  # "Pole dla ilości worków, wartość musi być co najmniej 1"
    categories = models.ManyToManyField(Category, verbose_name="Kategorie")  # "Pole wielu do wielu dla kategorii"
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='donations',
                                    verbose_name="Instytucja")  # "Pole klucza obcego dla instytucji, powiązane z darowiznami"
    address = models.CharField(max_length=255, verbose_name="Adres")  # "Pole dla adresu, maksymalna długość 255 znaków"
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                   message="Podaj prawidłowy numer telefonu w formacie: '+999999999'. Do 15 cyfr.")],
        verbose_name="Numer telefonu"
    )  # "Pole dla numeru telefonu, maksymalna długość 15 znaków, z walidacją formatu"
    city = models.CharField(max_length=255, verbose_name="Miasto")  # "Pole dla miasta, maksymalna długość 255 znaków"
    zip_code = models.CharField(max_length=10,
                                verbose_name="Kod pocztowy")  # "Pole dla kodu pocztowego, maksymalna długość 10 znaków"
    pick_up_date = models.DateField(verbose_name="Data odbioru")  # "Pole dla daty odbioru"
    pick_up_time = models.TimeField(verbose_name="Czas odbioru")  # "Pole dla czasu odbioru"
    pick_up_comment = models.TextField(blank=True, null=True,
                                       verbose_name="Komentarz do odbioru")  # "Pole dla komentarza do odbioru, może być puste"
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name="Użytkownik")  # "Pole klucza obcego dla użytkownika, może być puste"
    is_taken_by_user = models.BooleanField(default=False,
                                           verbose_name="Zabrane przez użytkownika")  # "Pole boolean dla zaznaczenia, czy darowizna została odebrana przez użytkownika"
    is_taken_by_courier = models.BooleanField(default=False,
                                              verbose_name="Zabrane przez kuriera")  # "Pole boolean dla zaznaczenia, czy darowizna została odebrana przez kuriera"
    courier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='courier_donations',
                                verbose_name="Kurier")  # "Pole klucza obcego dla kuriera, może być puste"
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending',
                              verbose_name="Status")  # "Pole dla statusu darowizny, z wyborem statusu"
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Utworzono")  # "Pole dla daty utworzenia, automatycznie ustawiane przy tworzeniu"
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name="Zaktualizowano")  # "Pole dla daty aktualizacji, automatycznie ustawiane przy każdej aktualizacji"

    class Meta:
        verbose_name = "Darowizna"  # "Pojedyncza darowizna"
        verbose_name_plural = "Darowizny"  # "Wiele darowizn"
        ordering = ['pick_up_date', 'pick_up_time']  # "Sortowanie darowizn według daty i czasu odbioru"
        indexes = [
            models.Index(fields=['pick_up_date', 'pick_up_time']),  # "Indeks na pola data i czas odbioru"
        ]

    def __str__(self):
        return f"Darowizna {self.quantity} worków od {self.user} do {self.institution}"  # "Reprezentacja darowizny jako ilość worków od użytkownika do instytucji"

    def clean(self):
        """
        Metoda czyszcząca model, sprawdza poprawność numeru telefonu.
        """
        if self.phone_number and not re.match(r'^\+?1?\d{9,15}$', self.phone_number):
            raise ValidationError(
                {
                    "phone_number": "Podaj prawidłowy numer telefonu w formacie: '+999999999'. Do 15 cyfr."})  # "Walidacja numeru telefonu"

    def save(self, *args, **kwargs):
        """
        Metoda zapisu modelu, wykonuje pełną walidację przed zapisaniem.
        """
        self.full_clean()  # "Walidacja przed zapisaniem"
        super().save(*args, **kwargs)  # "Wywołanie metody zapisu z klasy bazowej"

    def get_status_display(self):
        """
        Zwraca przetłumaczony status darowizny.
        """
        status_dict = dict(self.STATUS_CHOICES)
        return status_dict.get(self.status, self.status)  # "Metoda zwracająca przetłumaczony status darowizny"


class EmailVerificationToken(models.Model):
    """
    Model reprezentujący token weryfikacji email.

    Atrybuty:
        user (User): Użytkownik powiązany z tym tokenem.
        token (UUID): Unikalny token weryfikacyjny.
        created_at (datetime): Data utworzenia tokenu.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verification_token',
                                verbose_name="Użytkownik")  # "Pole klucza jednego do jednego dla użytkownika"
    token = models.UUIDField(default=uuid.uuid4, editable=False,
                             verbose_name="Token")  # "Pole dla tokenu UUID, automatycznie generowany"
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Utworzono")  # "Pole dla daty utworzenia, automatycznie ustawiane przy tworzeniu"

    def __str__(self):
        return f"{self.user.email} - {self.token}"  # "Reprezentacja tokenu jako email użytkownika i token"

    class Meta:
        verbose_name = "Token weryfikacji email"  # "Pojedynczy token weryfikacji email"
        verbose_name_plural = "Tokeny weryfikacji email"  # "Wiele tokenów weryfikacji email"


class PasswordResetToken(models.Model):
    """
    Model reprezentujący token resetowania hasła.

    Atrybuty:
        user (User): Użytkownik powiązany z tym tokenem.
        token (UUID): Unikalny token do resetowania hasła.
        created_at (datetime): Data utworzenia tokenu.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name="Użytkownik")  # "Pole klucza obcego dla użytkownika"
    token = models.UUIDField(default=uuid.uuid4, unique=True,
                             verbose_name="Token")  # "Pole dla unikalnego tokenu UUID, automatycznie generowany"
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Utworzono")  # "Pole dla daty utworzenia, automatycznie ustawiane przy tworzeniu"

    def __str__(self):
        return f"Token resetowania hasła dla {self.user.email}"  # "Reprezentacja tokenu jako token resetowania hasła dla email użytkownika"

    class Meta:
        verbose_name = "Token resetowania hasła"  # "Pojedynczy token resetowania hasła"
        verbose_name_plural = "Tokeny resetowania hasła"  # "Wiele tokenów resetowania hasła"


class ContactMessage(models.Model):
    """
    Model reprezentujący wiadomość kontaktową.

    Atrybuty:
        name (str): Imię nadawcy wiadomości.
        surname (str): Nazwisko nadawcy wiadomości.
        email (str): Email nadawcy wiadomości.
        message (str): Treść wiadomości.
        created_at (datetime): Data utworzenia wiadomości.
    """
    name = models.CharField(max_length=255,
                            verbose_name="Imię")  # "Pole dla imienia nadawcy, maksymalna długość 255 znaków"
    surname = models.CharField(max_length=255,
                               verbose_name="Nazwisko")  # "Pole dla nazwiska nadawcy, maksymalna długość 255 znaków"
    email = models.EmailField(verbose_name="Email")  # "Pole dla email nadawcy"
    message = models.TextField(verbose_name="Wiadomość")  # "Pole dla treści wiadomości"
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Utworzono")  # "Pole dla daty utworzenia wiadomości, automatycznie ustawiane przy tworzeniu"

    class Meta:
        verbose_name = "Wiadomość kontaktowa"  # "Pojedyncza wiadomość kontaktowa"
        verbose_name_plural = "Wiadomości kontaktowe"  # "Wiele wiadomości kontaktowych"
        ordering = ['-created_at']  # "Sortowanie wiadomości według daty utworzenia, od najnowszej"

    def __str__(self):
        return f"Wiadomość od {self.name} {self.surname} ({self.email})"  # "Reprezentacja wiadomości jako wiadomość od imię nazwisko (email)"


class ProblemReport(models.Model):
    TOPIC_CHOICES = [
        ('bug', 'Błąd'),
        ('feature', 'Prośba o funkcję'),
        ('usability', 'Użyteczność'),
        ('performance', 'Wydajność'),
        ('security', 'Bezpieczeństwo'),
        ('other', 'Inne'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Użytkownik")
    topic = models.CharField(max_length=20, choices=TOPIC_CHOICES, verbose_name="Temat")
    message = models.TextField(verbose_name="Wiadomość")
    browser_info = models.CharField(max_length=255, blank=True, verbose_name="Informacje o przeglądarce")
    operating_system = models.CharField(max_length=255, blank=True, verbose_name="System operacyjny")
    steps_to_reproduce = models.TextField(blank=True, verbose_name="Kroki do odtworzenia")
    screenshot = models.ImageField(upload_to='problem_reports/', blank=True, null=True, verbose_name="Zrzut ekranu")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data zgłoszenia")

    class Meta:
        verbose_name = "Zgłoszenie problemu"
        verbose_name_plural = "Zgłoszenia problemów"
        ordering = ['-created_at']

    def __str__(self):
        return f"Zgłoszenie od {self.user.username} - {self.get_topic_display()}"
