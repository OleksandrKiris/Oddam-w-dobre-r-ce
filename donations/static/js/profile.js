// Funkcja do pobierania wartości ciasteczka o podanej nazwie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        // Rozdzielenie ciasteczek na poszczególne elementy
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Sprawdzanie, czy nazwa ciasteczka odpowiada podanej nazwie
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                // Dekodowanie wartości ciasteczka
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Funkcja do przełączania archiwizacji darowizny
function toggleArchive(donationId, userType) {
    const csrftoken = getCookie('csrftoken'); // Pobieranie tokenu CSRF

    fetch("/user_profile/", {
        method: 'POST', // Metoda POST do wysyłania danych
        headers: {
            'Content-Type': 'application/json', // Typ treści
            'X-CSRFToken': csrftoken // Nagłówek tokenu CSRF
        },
        body: JSON.stringify({ donation_id: donationId, user_type: userType }) // Przesyłanie danych w formacie JSON
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.message); }); // Obsługa błędów odpowiedzi
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            const row = document.querySelector(`.donation-row[data-donation-id='${donationId}']`); // Znajdowanie wiersza darowizny
            row.classList.toggle('archived'); // Przełączanie klasy 'archived'
            const buttonUser = row.querySelector('.btn-archive-user'); // Znajdowanie przycisku archiwizacji użytkownika
            if (data.is_taken_by_user) {
                buttonUser.textContent = 'Oznacz jako niezabrane przez użytkownika'; // Aktualizacja tekstu przycisku
            } else {
                buttonUser.textContent = 'Oznacz jako zabrane przez użytkownika'; // Aktualizacja tekstu przycisku
            }
        } else {
            alert(data.message); // Wyświetlanie komunikatu o błędzie
        }
    })
    .catch(error => {
        alert('Wystąpił błąd podczas aktualizacji statusu darowizny. Spróbuj ponownie. ' + error.message); // Obsługa błędów
    });
}

// Funkcja do konfiguracji linków paginacji
function setupPaginationLinks() {
    document.querySelectorAll('.pagination-link').forEach(link => {
        link.addEventListener('click', (event) => {
            event.preventDefault(); // Zatrzymanie domyślnego działania linku
            const url = event.target.href;
            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest' // Nagłówek do żądania AJAX
                }
            })
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html'); // Parsowanie odpowiedzi HTML
                const newTableContainer = doc.querySelector('#donations-table-container'); // Znajdowanie nowego kontenera tabeli
                if (newTableContainer) {
                    document.querySelector('#donations-table-container').innerHTML = newTableContainer.innerHTML; // Aktualizacja kontenera tabeli
                    setupPaginationLinks(); // Ponowna konfiguracja linków paginacji
                    window.scrollTo({
                        top: document.querySelector('#donations-table-container').offsetTop,
                        behavior: 'smooth' // Płynne przewijanie do tabeli
                    });
                }
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error); // Logowanie błędów
            });
        });
    });
}

// Zdarzenie DOMContentLoaded do konfiguracji linków paginacji po załadowaniu strony
document.addEventListener('DOMContentLoaded', () => {
    setupPaginationLinks();
});
