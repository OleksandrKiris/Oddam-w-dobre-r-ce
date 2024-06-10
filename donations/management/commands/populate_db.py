import os
import random
import uuid
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from faker import Faker
from donations.models import Category, Institution, Donation, EmailVerificationToken, PasswordResetToken, ContactMessage

# Konfiguracja ustawień Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'charity_platform.settings')

import django

django.setup()

# Używamy polskiej lokalizacji dla Faker
fake = Faker('pl_PL')

PASSWORD = 'Kibel123456ok'
NUM_USERS = 100
NUM_SUPERUSERS = 20
NUM_INSTITUTIONS = 50
NUM_DONATIONS_PER_USER = 50
NUM_CONTACT_MESSAGES = 200
CATEGORIES = ['Odzież', 'Żywność', 'Zabawki', 'Książki', 'Sprzęt AGD']


class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Usuwanie starych danych...')
        models = [Donation, Institution, Category, User, EmailVerificationToken, PasswordResetToken, ContactMessage]
        for model in models:
            model.objects.all().delete()

        # Tworzenie kategorii
        self.stdout.write('Tworzenie kategorii...')
        category_instances = [Category.objects.create(name=name) for name in CATEGORIES]

        # Tworzenie instytucji
        self.stdout.write('Tworzenie instytucji...')
        institutions = []
        for _ in range(NUM_INSTITUTIONS):
            institution = Institution.objects.create(
                name=fake.company(),
                description=fake.text(),
                type=random.choice([Institution.FOUNDATION, Institution.NGO, Institution.LOCAL_COLLECTION]),
                created_at=timezone.now()
            )
            institution.categories.set(random.sample(category_instances, random.randint(1, len(category_instances))))
            institutions.append(institution)

        # Tworzenie użytkowników i darowizn
        self.stdout.write('Tworzenie użytkowników i darowizn...')
        users = []
        for i in range(NUM_USERS):
            email = fake.email()
            first_name = fake.first_name()
            last_name = fake.last_name()
            user = User.objects.create_user(username=email, email=email, password=PASSWORD)
            user.first_name = first_name
            user.last_name = last_name
            user.is_superuser = i < NUM_SUPERUSERS  # Pierwszych NUM_SUPERUSERS użytkowników będzie superużytkownikami
            user.is_staff = True if i < NUM_SUPERUSERS else False  # Pierwszych NUM_SUPERUSERS użytkowników będzie także pracownikami
            user.save()
            users.append(user)

            for _ in range(NUM_DONATIONS_PER_USER):
                phone_number = '+48' + fake.msisdn()[2:11]  # Polski numer telefonu zaczynający się od +48

                donation = Donation.objects.create(
                    quantity=random.randint(1, 10),
                    institution=random.choice(institutions),
                    address=fake.address(),
                    phone_number=phone_number,
                    city=fake.city(),
                    zip_code=fake.zipcode(),
                    pick_up_date=fake.date_this_year(),
                    pick_up_time=fake.time(),
                    pick_up_comment=fake.sentence(),
                    user=user,
                    is_taken_by_user=random.choice([True, False]),
                    is_taken_by_courier=random.choice([True, False]),
                    courier=random.choice(users) if random.choice([True, False]) else None,
                    status=random.choice([status for status, _ in Donation.STATUS_CHOICES]),
                    created_at=timezone.now(),
                    updated_at=timezone.now()
                )
                donation.categories.set(random.sample(category_instances, random.randint(1, len(category_instances))))

        # Tworzenie tokenów weryfikacji email
        self.stdout.write('Tworzenie tokenów weryfikacji email...')
        for user in users:
            EmailVerificationToken.objects.create(user=user, token=uuid.uuid4(), created_at=timezone.now())

        # Tworzenie tokenów resetowania hasła
        self.stdout.write('Tworzenie tokenów resetowania hasła...')
        for user in users:
            PasswordResetToken.objects.create(user=user, token=uuid.uuid4(), created_at=timezone.now())

        # Tworzenie wiadomości kontaktowych
        self.stdout.write('Tworzenie wiadomości kontaktowych...')
        for _ in range(NUM_CONTACT_MESSAGES):
            ContactMessage.objects.create(
                name=fake.first_name(),
                surname=fake.last_name(),
                email=fake.email(),
                message=fake.text(),
                created_at=timezone.now()
            )

        self.stdout.write(self.style.SUCCESS('Pomyślnie wypełniono bazę danych.'))
