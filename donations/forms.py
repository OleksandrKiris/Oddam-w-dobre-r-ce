from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'surname', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Imię', 'class': 'form-control contact-input'}),
            'surname': forms.TextInput(attrs={'placeholder': 'Nazwisko', 'class': 'form-control contact-input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control contact-input'}),
            'message': forms.Textarea(attrs={'placeholder': 'Wiadomość', 'rows': 4, 'class': 'form-control contact-input'}),
        }
        error_messages = {
            'name': {
                'required': 'Proszę wpisać imię.',
            },
            'surname': {
                'required': 'Proszę wpisać nazwisko.',
            },
            'email': {
                'required': 'Proszę wpisać email.',
                'invalid': 'Proszę wpisać poprawny email.',
            },
            'message': {
                'required': 'Proszę wpisać wiadomość.',
            },
        }


