# Ticketify

Nowoczesny, lekki system zarządzania zgłoszeniami oparty na Flask. Idealny dla małych i średnich zespołów, które potrzebują prostego, a zarazem wydajnego rozwiązania do śledzenia zgłoszeń pomocy technicznej, raportów o błędach i próśb wewnętrznych.

## Funkcje

### Obsługa wielu firm
- **Tworzenie firmy**: Twórz nowe firmy z unikalnymi identyfikatorami UUID
- **Dołączanie do zespołu**: Dołącz do istniejących firm za pomocą identyfikatora UUID firmy
- **Izolowane obszary robocze**: Każda firma ma całkowicie oddzielne obszary zgłoszeń

### Kontrola dostępu oparta na rolach
- **Administratorzy**: Pełny dostęp do wszystkich zgłoszeń firmowych z możliwością zarządzania
- **Użytkownicy**: Mogą tworzyć, przeglądać i zarządzać własnymi zgłoszeniami

### Zarządzanie zgłoszeniami
- **Tworzenie zgłoszeń**: Proste tworzenie zgłoszeń za pomocą formularza
- **Śledzenie statusu**: Status Otwarte/Zamknięte ze wskaźnikami wizualnymi
- **Komentarze administratora**: Administratorzy mogą dodawać komentarze dotyczące zamknięcia
- **Usuwanie zgłoszeń**: Użytkownicy mogą usuwać własne zgłoszenia, administratorzy mogą usuwać dowolne
- **Inteligentne sortowanie**: Zawsze otwarte zgłoszenia Wyświetlaj najpierw, a następnie sortuj według daty utworzenia

### Nowoczesny UI/UX
- **Responsywny projekt**: Stworzony w Tailwind CSS dla środowiska mobilnego
- **Elementy interaktywne**: Rozwijane szczegóły zgłoszenia z płynnymi przejściami
- **Wskaźniki statusu**: Kolorowe znaczniki statusu dla szybkiego odniesienia wizualnego
- **Przejrzysty interfejs**: Profesjonalny, nierozpraszający uwagi projekt

## Szybki start

### Wymagania

- Python 3.11
- Flask & Serwer WSGI Waitress (w `requirements.txt`)
- Docker (opcjonalnie)

### Lokalne wdrożenie

1. **Klonowanie repozytorium**
```bash
git clone https://github.com/yourusername/ticketify.git
cd ticketify
```

2. **Instalacja zależności**
```bash
pip install -r requirements.txt
```

3. **Uruchomianie aplikacji**
```bash
python app.py
```

4. **Uzyskanie dostępu do aplikacji**\
Otwórz przeglądarkę i przejdź do `http://localhost:5000`

### Konteneryzacja

1. **Zbuduj obraz**
```bash
docker build -t ticketify .
```

2. **Uruchom kontener**
```bash
docker run -p 5000:5000 ticketify
```

## Architektura

### Schemat bazy danych

Aplikacja korzysta z bazy danych SQLite z trzema głównymi tabelami:

- **companies**: Przechowuje informacje o firmie z unikalnymi identyfikatorami UUID
- **users**: Konta użytkowników z uprawnieniami opartymi na rolach i powiązaniami firmowymi
- **tickets**: Dane zgłoszeń ze śledzeniem statusu i metadanymi

### Funkcje bezpieczeństwa

- **Bezpieczeństwo haseł**: Wszystkie hasła są hashowane za pomocą narzędzi bezpieczeństwa Werkzeug
- **Zarządzanie sesjami**: Bezpieczna obsługa sesji dzięki wbudowanemu zarządzaniu sesjami Flask
- **Nagłówki bezpieczeństwa**: Implementuje nagłówki bezpieczeństwa, w tym `X-Content-Type-Options` i `Referrer-Policy`
- **Walidacja danych wejściowych**: Walidacja po stronie serwera dla wszystkich danych wprowadzanych przez użytkownika
- **Kontrola autoryzacji**: Prawidłowe sprawdzanie autoryzacji dla wszystkich wrażliwych operacji

## Instrukcja obsługi

### Wprowadzenie

1. **Zarejestruj konto**: Wybierz, czy chcesz utworzyć nową firmę, czy dołączyć do istniejącej, używając firmowego identyfikatora UUID
2. **Logowanie**: Użyj swoich danych uwierzytelniających, aby uzyskać dostęp do systemu
3. **Tworzenie zgłoszeń**: Prześlij nowe zgłoszenia z tytułem i szczegółowym opisem
4. **Śledzenie postępów**: Monitoruj status zgłoszeń i odpowiedzi administratorów

### Dla administratorów

- **Zarządzanie firmą**: Pierwszy użytkownik, który utworzy firmę, automatycznie zostaje administratorem
- **Przegląd zgłoszeń**: Przeglądaj wszystkie zgłoszenia od członków firmy w scentralizowanym panelu
- **Rozwiązywanie zgłoszeń**: Zamykaj zgłoszenia z opcjonalnymi komentarzami dla użytkowników
- **Zarządzanie użytkownikami**: Monitoruj aktywność użytkowników i wzorce zgłoszeń

### Dla zwykłych użytkowników

- **Pulpit osobisty**: Przeglądaj tylko własne zgłoszenia z przejrzystymi wskaźnikami statusu
- **Tworzenie zgłoszeń**: Łatwy w użyciu Formularz do przesyłania nowych zgłoszeń
- **Samoobsługa**: Usuń własne zgłoszenia, gdy nie są już potrzebne
- **Aktualizacje statusu**: Otrzymuj informacje zwrotne poprzez komentarze administratora dotyczące zamkniętych zgłoszeń