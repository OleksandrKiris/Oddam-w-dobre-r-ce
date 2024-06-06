# donations/models.py
import uuid

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import re


class Category(models.Model):
    # Nazwa kategorii, unikalna wartość
    name = models.CharField(max_length=255, unique=True, verbose_name="Nazwa")

    class Meta:
        verbose_name = "Kategoria"
        verbose_name_plural = "Kategorie"
        ordering = ['name']

    def __str__(self):
        return self.name


class Institution(models.Model):
    # Definicje typów instytucji
    FOUNDATION = 'fundacja'
    NGO = 'organizacja pozarządowa'
    LOCAL_COLLECTION = 'zbiórka lokalna'

    TYPE_CHOICES = [
        (FOUNDATION, 'Fundacja'),
        (NGO, 'Organizacja pozarządowa'),
        (LOCAL_COLLECTION, 'Zbiórka lokalna'),
    ]

    # Nazwa instytucji, unikalna wartość
    name = models.CharField(max_length=255, unique=True, verbose_name="Nazwa")
    # Opis instytucji
    description = models.TextField(verbose_name="Opis")
    # Typ instytucji
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default=FOUNDATION, verbose_name="Typ")
    # Kategorie związane z instytucją
    categories = models.ManyToManyField(Category, verbose_name="Kategorie")

    class Meta:
        verbose_name = "Instytucja"
        verbose_name_plural = "Instytucje"
        ordering = ['name']

    def __str__(self):
        return self.name


class Donation(models.Model):
    # Ilość worków
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="Ilość worków")
    # Kategorie daru
    categories = models.ManyToManyField(Category, verbose_name="Kategorie")
    # Instytucja związана с darem
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, verbose_name="Instytucja")
    # Adres odbioru daru
    address = models.CharField(max_length=255, verbose_name="Adres")
    # Numer telefonu
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')],
        verbose_name="Numer telefonu"
    )
    # Miasto
    city = models.CharField(max_length=255, verbose_name="Miasto")
    # Kod pocztowy
    zip_code = models.CharField(max_length=10, verbose_name="Kod pocztowy")
    # Data odbioru daru
    pick_up_date = models.DateField(verbose_name="Data odbioru")
    # Czas odbiorу darу
    pick_up_time = models.TimeField(verbose_name="Czas odbiorу")
    # Komентарz до odbiorу дару
    pick_up_comment = models.TextField(blank=True, null=True, verbose_name="Komentarz do odbiorу")
    # Użytkownik związany с darem
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Użytkownik")
    # Поле для обозначения, что дар был забран
    is_taken = models.BooleanField(default=False, verbose_name="Zabrany")

    class Meta:
        verbose_name = "Darowizna"
        verbose_name_plural = "Darowizny"
        ordering = ['pick_up_date', 'pick_up_time']

    def __str__(self):
        return f"Darowizna {self.quantity} worków od {self.user} do {self.institution}"

    def clean(self):
        # Sprawdzenie czy data odbiorу nie jest w przeszłości
        if self.pick_up_date < timezone.now().date():
            raise ValidationError("Data odbiorу nie może być w przeszłości.")

        # Sprawdzenie formatu numeru telefonu
        if self.phone_number and not re.match(r'^\+?1?\d{9,15}$', self.phone_number):
            raise ValidationError("Podaj prawidłowy numer telefonu.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Wykonanie walidacji przed zapisaniem
        super().save(*args, **kwargs)


class EmailVerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verification_token')
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.token}"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset token for {self.user.email}"
