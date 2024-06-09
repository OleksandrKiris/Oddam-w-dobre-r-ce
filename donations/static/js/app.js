document.addEventListener("DOMContentLoaded", function() {
  // Klasa obsługująca kroki formularza
  class FormSteps {
    constructor(form) {
      this.$form = form;  // Formularz
      this.$next = form.querySelectorAll(".next-step");  // Przyciski "następny krok"
      this.$prev = form.querySelectorAll(".prev-step");  // Przyciski "poprzedni krok"
      this.$step = form.querySelector(".form--steps-counter span");  // Licznik kroków
      this.currentStep = 1;  // Bieżący krok

      this.$stepInstructions = form.querySelectorAll(".form--steps-instructions p");  // Instrukcje dla kroków
      const $stepForms = form.querySelectorAll("form > div");  // Wszystkie sekcje formularza
      this.slides = [...this.$stepInstructions, ...$stepForms];  // Łączenie instrukcji z sekcjami formularza

      this.init();  // Inicjalizacja klasy
    }

    // Inicjalizacja zdarzeń i aktualizacja formularza
    init() {
      this.events();  // Ustawienie zdarzeń
      this.updateForm();  // Aktualizacja formularza
    }

    // Ustawienie nasłuchiwania zdarzeń
    events() {
      // Zdarzenia dla przycisków "następny krok"
      this.$next.forEach(btn => {
        btn.addEventListener("click", e => {
          e.preventDefault();  // Zatrzymanie domyślnego działania przycisku
          if (this.validateStep()) {  // Walidacja bieżącego kroku
            this.currentStep++;  // Przejście do następnego kroku
            this.updateForm();  // Aktualizacja formularza
          }
        });
      });

      // Zdarzenia dla przycisków "poprzedni krok"
      this.$prev.forEach(btn => {
        btn.addEventListener("click", e => {
          e.preventDefault();  // Zatrzymanie domyślnego działania przycisku
          if (this.currentStep > 1) {  // Sprawdzenie, czy nie jest to pierwszy krok
            this.currentStep--;  // Powrót do poprzedniego kroku
            this.updateForm();  // Aktualizacja formularza
          }
        });
      });

      // Zdarzenie dla przesyłania formularza
      this.$form.querySelector("form").addEventListener("submit", e => this.submit(e));

      // Zdarzenia dla zmiany checkboxów kategorii
      document.querySelectorAll('.category-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', () => {
          this.filterInstitutions();  // Filtrowanie instytucji
        });
      });
    }

    // Walidacja bieżącego kroku formularza
    validateStep() {
      if (this.currentStep === 4) {  // Walidacja dla kroku 4
        const phoneInput = document.querySelector('input[name="phone"]');  // Pole numeru telefonu
        const phoneValue = phoneInput ? phoneInput.value : '';  // Wartość numeru telefonu
        const phoneRegex = /^\+?1?\d{9,15}$/;  // Wyrażenie regularne dla walidacji numeru telefonu
        if (!phoneRegex.test(phoneValue)) {  // Sprawdzenie, czy numer telefonu jest poprawny
          alert("Podaj prawidłowy numer telefonu w formacie: '+999999999'. Do 15 cyfr.");  // Alert o błędzie
          return false;
        }
      }
      return true;  // Walidacja zakończona pomyślnie
    }

    // Aktualizacja formularza
    updateForm() {
      if (this.$step) {
        this.$step.innerText = this.currentStep;  // Aktualizacja licznika kroków
      }

      this.slides.forEach(slide => {
        slide.classList.remove("active");  // Usuwanie klasy "active" z każdego slajdu

        if (parseInt(slide.dataset.step) === this.currentStep) {  // Sprawdzenie, czy krok się zgadza
          slide.classList.add("active");  // Dodanie klasy "active" do bieżącego slajdu
        }
      });

      const stepInstructionsContainer = this.$stepInstructions[0]?.parentElement?.parentElement;  // Kontener instrukcji kroków
      if (stepInstructionsContainer) {
        stepInstructionsContainer.hidden = this.currentStep >= 6;  // Ukrywanie instrukcji po kroku 6
      }

      if (this.$step) {
        this.$step.parentElement.hidden = this.currentStep >= 6;  // Ukrywanie licznika kroków po kroku 6
      }

      if (this.currentStep === 5) {
        this.showSummary();  // Pokazywanie podsumowania na kroku 5
      }
    }

    // Filtrowanie instytucji na podstawie zaznaczonych kategorii
    filterInstitutions() {
      const selectedCategories = [...document.querySelectorAll('.category-checkbox:checked')].map(cb => parseInt(cb.value));  // Pobieranie zaznaczonych kategorii
      document.querySelectorAll('.institution').forEach(inst => {
        const instCategories = inst.dataset.categories ? inst.dataset.categories.split(',').map(Number) : [];  // Pobieranie kategorii instytucji
        const match = selectedCategories.every(cat => instCategories.includes(cat));  // Sprawdzanie dopasowania kategorii
        inst.style.display = match ? 'block' : 'none';  // Wyświetlanie lub ukrywanie instytucji
      });
    }

    // Pokazywanie podsumowania
    showSummary() {
      const selectedInstitutionElement = document.querySelector('input[name="organization"]:checked');  // Zaznaczona organizacja
      const selectedInstitution = selectedInstitutionElement ? selectedInstitutionElement.nextElementSibling.querySelector('.title')?.innerText : '';  // Nazwa zaznaczonej organizacji

      // Elementy podsumowania
      const summaryItems = [
        { selector: '.summary .icon-bag + .summary--text', text: `${document.querySelector('input[name="bags"]')?.value} worki ubrań` },
        { selector: '.summary .icon-hand + .summary--text', text: `Dla fundacji ${selectedInstitution}` },
        { selector: '.summary .address', text: document.querySelector('input[name="address"]')?.value },
        { selector: '.summary .city', text: document.querySelector('input[name="city"]')?.value },
        { selector: '.summary .postcode', text: document.querySelector('input[name="postcode"]')?.value },
        { selector: '.summary .phone', text: document.querySelector('input[name="phone"]')?.value },
        { selector: '.summary .date', text: document.querySelector('input[name="date"]')?.value },
        { selector: '.summary .time', text: document.querySelector('input[name="time"]')?.value },
        { selector: '.summary .more_info', text: document.querySelector('textarea[name="more_info"]')?.value || 'Brak uwag' }
      ];

      summaryItems.forEach(item => {
        const element = document.querySelector(item.selector);  // Znajdowanie elementu w podsumowaniu
        if (element) {
          element.innerText = item.text;  // Ustawianie tekstu podsumowania
        } else {
          console.warn(`Element ${item.selector} nie istnieje na stronie`);  // Ostrzeżenie, jeśli element nie istnieje
        }
      });
    }

    // Obsługa przesyłania formularza
    async submit(e) {
      e.preventDefault();  // Zatrzymanie domyślnego działania formularza
      if (this.currentStep < 5) {
        this.currentStep++;  // Przejście do następnego kroku, jeśli bieżący krok jest mniejszy niż 5
        this.updateForm();  // Aktualizacja formularza
      } else {
        const formData = new FormData(this.$form.querySelector('form'));  // Pobieranie danych z formularza

        try {
          const response = await fetch(this.$form.querySelector('form').action, {
            method: 'POST',
            body: formData,
            headers: {
              'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,  // Dodanie tokenu CSRF
            }
          });

          if (!response.ok) {
            throw new Error('Network response was not ok');  // Rzucenie błędu w przypadku problemu z siecią
          }

          window.location.href = '/form_success';  // Przekierowanie po pomyślnym przesłaniu formularza
        } catch (error) {
          console.error('Wystąpił problem z operacją fetch:', error);  // Logowanie błędu
          alert('Wystąpił błąd podczas przesyłania formularza. Spróbuj ponownie.');  // Alert o błędzie
        }
      }
    }
  }

  // Inicjalizacja klasy FormSteps, jeśli formularz istnieje na stronie
  const form = document.querySelector(".form--steps");
  if (form) {
    new FormSteps(form);
  }
});
