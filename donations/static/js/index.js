document.addEventListener("DOMContentLoaded", function() {
  // Znajdowanie elementu dropdown na stronie
  const dropdown = document.querySelector('.dropdown');
  if (dropdown) {
    // Dodanie zdarzenia 'mouseenter' dla dropdown
    dropdown.addEventListener('mouseenter', () => {
      dropdown.querySelector('.dropdown-content').style.display = 'block';  // Pokazywanie zawartości dropdown
    });
    // Dodanie zdarzenia 'mouseleave' dla dropdown
    dropdown.addEventListener('mouseleave', () => {
      dropdown.querySelector('.dropdown-content').style.display = 'none';  // Ukrywanie zawartości dropdown
    });
  }

  // Znajdowanie wszystkich przycisków zakładek oraz zakładek na stronie
  const tabButtons = document.querySelectorAll('.help--buttons a');
  const tabs = document.querySelectorAll('.help--slides');
  // Pobieranie aktywnej zakładki z sessionStorage lub ustawienie domyślnej wartości
  let activeTab = sessionStorage.getItem('activeTab') || 'foundations';

  // Funkcja do pokazywania odpowiedniej zakładki
  function showTab(target) {
    tabs.forEach(tab => {
      if (tab.dataset.id === target) {
        tab.classList.add('active');  // Dodawanie klasy 'active' dla odpowiedniej zakładki
      } else {
        tab.classList.remove('active');  // Usuwanie klasy 'active' dla innych zakładek
      }
    });
    tabButtons.forEach(btn => {
      if (btn.dataset.target === target) {
        btn.classList.add('active');  // Dodawanie klasy 'active' dla odpowiedniego przycisku zakładki
      } else {
        btn.classList.remove('active');  // Usuwanie klasy 'active' dla innych przycisków zakładek
      }
    });
  }

  // Wywołanie funkcji showTab dla aktywnej zakładki po załadowaniu strony
  showTab(activeTab);

  // Dodanie zdarzeń 'click' dla przycisków zakładek
  tabButtons.forEach(button => {
    button.addEventListener('click', (event) => {
      event.preventDefault();  // Zatrzymanie domyślnego działania linku
      const target = event.target.dataset.target;  // Pobieranie celu z atrybutu data-target
      sessionStorage.setItem('activeTab', target);  // Zapisywanie aktywnej zakładki w sessionStorage
      showTab(target);  // Wywołanie funkcji showTab dla wybranej zakładki
      activeTab = target;  // Ustawienie aktywnej zakładki
    });
  });

  // Dodanie zdarzeń 'click' dla linków paginacji
  const paginationLinks = document.querySelectorAll('.pagination a');
  paginationLinks.forEach(link => {
    link.addEventListener('click', (event) => {
      const url = new URL(event.target.href);  // Tworzenie nowego URL z href linku
      url.searchParams.set('activeTab', activeTab);  // Dodawanie aktywnej zakładki do parametrów URL
      event.target.href = url.toString();  // Ustawienie nowego href z dodaną aktywną zakładką
    });
  });
});
