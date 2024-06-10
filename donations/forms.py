from django import forms
from .models import ContactMessage, ProblemReport


# Formularz kontaktowy
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage  # Model reprezentujący wiadomości kontaktowe
        fields = ['name', 'surname', 'email', 'message']  # Pola formularza

        # Konfiguracja widżetów dla pól formularza
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Imię', 'class': 'form-control contact-input'}),
            # Widżet dla pola imię
            'surname': forms.TextInput(attrs={'placeholder': 'Nazwisko', 'class': 'form-control contact-input'}),
            # Widżet dla pola nazwisko
            'email': forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control contact-input'}),
            # Widżet dla pola email
            'message': forms.Textarea(
                attrs={'placeholder': 'Wiadomość', 'rows': 4, 'class': 'form-control contact-input'}),
            # Widżet dla pola wiadomość
        }

        # Wiadomości o błędach walidacji pól formularza
        error_messages = {
            'name': {
                'required': 'Proszę wpisać imię.',  # Wiadomość o błędzie dla pola imię
            },
            'surname': {
                'required': 'Proszę wpisać nazwisko.',  # Wiadomość o błędzie dla pola nazwisko
            },
            'email': {
                'required': 'Proszę wpisać email.',  # Wiadomość o błędzie dla pola email
                'invalid': 'Proszę wpisać poprawny email.',  # Wiadomość o błędzie dla niepoprawnego formatu email
            },
            'message': {
                'required': 'Proszę wpisać wiadomość.',  # Wiadomość o błędzie dla pola wiadomość
            },
        }


# Formularz zgłoszenia problemu
class ProblemReportForm(forms.ModelForm):
    class Meta:
        model = ProblemReport  # Model reprezentujący zgłoszenia problemów
        fields = ['topic', 'message', 'browser_info', 'operating_system', 'steps_to_reproduce',
                  'screenshot']  # Pola formularza

        # Konfiguracja widżetów dla pól formularza
        widgets = {
            'topic': forms.Select(attrs={'class': 'form-control'}),  # Widżet dla pola temat
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),  # Widżet dla pola wiadomość
            'browser_info': forms.TextInput(attrs={'class': 'form-control'}),
            # Widżet dla pola informacje o przeglądarce
            'operating_system': forms.TextInput(attrs={'class': 'form-control'}),  # Widżet dla pola system operacyjny
            'steps_to_reproduce': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            # Widżet dla pola kroki do odtworzenia
            'screenshot': forms.ClearableFileInput(attrs={'class': 'form-control'}),  # Widżet dla pola zrzut ekranu
        }

        # Etykiety dla pól formularza
        labels = {
            'topic': 'Temat',  # Etykieta dla pola temat
            'message': 'Wiadomość',  # Etykieta dla pola wiadomość
            'browser_info': 'Informacje o przeglądarce',  # Etykieta dla pola informacje o przeglądarce
            'operating_system': 'System operacyjny',  # Etykieta dla pola system operacyjny
            'steps_to_reproduce': 'Kroki do odtworzenia',  # Etykieta dla pola kroki do odtworzenia
            'screenshot': 'Zrzut ekranu',  # Etykieta dla pola zrzut ekranu
        }
