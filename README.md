# LOK LAUNCHER — development build 0.2.0

Lekki launcher Minecraft Java dla Windows (kod Python/Tkinter).

## Co działa w tej wersji
- wykrywanie CPU, RAM, GPU (Windows), systemu i typu dysku;
- profile optymalizacji LIGHT / BALANCED / PERFORMANCE;
- lista wersji Minecrafta z oficjalnego manifestu;
- instalacja Vanilla oraz Fabric, Forge, NeoForge i Quilt przez `minecraft-launcher-lib`;
- wybór ilości RAM i katalogu gry;
- interfejs Tkinter, operacje sieciowe wykonywane w tle;
- logi i zapisywanie ustawień.

## Ważne ograniczenie logowania
Uruchamianie gry wymaga legalnego konta Microsoft posiadającego Minecraft Java. Integracja OAuth Microsoft wymaga własnego identyfikatora aplikacji (Client ID) skonfigurowanego w Microsoft Entra. Ta wersja przygotowuje menedżer instalacji i sprzętu; przycisk uruchamiania uczciwie informuje, że moduł konta nie jest jeszcze skonfigurowany. Nie ma trybu cracked/offline.

## Uruchomienie (Windows 10/11)
1. Zainstaluj Python 3.11 lub nowszy z python.org i zaznacz **Add Python to PATH**.
2. Rozpakuj projekt.
3. Uruchom `install_and_run.bat`.
   Albo ręcznie:
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   py -m pip install -r requirements.txt
   py main.py
   ```

Minecraft wymaga odpowiedniej wersji Java. Biblioteka launchera zarządza instalacją plików gry; Java może być dostarczana przez oficjalne runtime'y Minecrafta lub wymagać konfiguracji zależnie od wersji.

## Struktura
- `main.py` — start aplikacji
- `assets/lok_hero.png` — grafika głównego ekranu
- `lok_launcher/ui.py` — odświeżony interfejs
- `lok_launcher/core.py` — instalacja i wersje
- `lok_launcher/hardware.py` — diagnostyka sprzętu
- `lok_launcher/optimizer.py` — bezpieczne rekomendacje
- `lok_launcher/config.py` — konfiguracja lokalna

## Zasady optymalizacji
LOK nie wyłącza usług Windows, nie zabija procesów i nie zmienia rejestru. Ustawia wyłącznie parametry Minecrafta i pokazuje rekomendacje. Przydział RAM jest ograniczany do bezpiecznej części pamięci dostępnej w systemie. Zmiana render distance / grafiki odbywa się w grze, a nie przez nieudokumentowane modyfikacje.

## Następne etapy
1. Microsoft OAuth PKCE i bezpieczne odświeżanie tokenów.
2. Właściwe uruchamianie procesu Minecraft i konsola gry.
3. Zarządzanie instancjami, modami i paczkami `.mrpack`.
4. Testy na Windows 10/11 i starszym sprzęcie.
5. Pakowanie do instalatora `.exe`.


## Samodzielny plik EXE (Windows)
Na komputerze deweloperskim uruchom `build_windows.bat`. Skrypt zainstaluje
PyInstaller i zbuduje aplikację bez konsoli. Gotowy plik będzie tutaj:

`dist\\LOK Launcher\\LOK Launcher.exe`

Do uruchamiania gotowego programu nie trzeba instalować Pythona. Należy
jednak skopiować cały folder `LOK Launcher` z `dist`, ponieważ zawiera
biblioteki i zasoby aplikacji. Budowanie EXE musi odbyć się na Windows;
w tym środowisku przygotowano skrypt, ale nie wykonano kompilacji Windows EXE.

Dla szybszego startu i prostszych aktualizacji używany jest tryb `onedir`,
a nie `onefile`. Okno uruchamia się bez konsoli systemowej.


## Folder gry i instalator Windows
LOK Launcher domyślnie korzysta ze standardowego `%APPDATA%\\.minecraft`.
Przy pierwszym uruchomieniu pojawia się konfiguracja folderu gry: można
zaakceptować standardowy katalog albo wskazać istniejący folder `.minecraft`
(np. na innym dysku). Launcher nie kasuje światów, modów ani innych danych.

Sam program instaluje się oddzielnie w `Program Files\\LOK Launcher`.
Odinstalowanie aplikacji nie powinno usuwać katalogu `.minecraft`.

### Utworzenie instalatora Setup.exe
1. Uruchom `build_windows.bat` na Windows.
2. Zainstaluj Inno Setup 6.
3. Otwórz `installer.iss` w Inno Setup Compiler i kliknij Compile.
4. Instalator powstanie w `installer_output`.

`installer.iss` pakuje cały folder `dist\\LOK Launcher`; nie należy kopiować
samego EXE bez pozostałych plików aplikacji.


## Gotowy instalator bez Pythona na komputerze użytkownika
ZIP źródłowy nie jest sam w sobie instalatorem. Dodano workflow GitHub Actions,
który buduje Windows EXE i Setup.exe na maszynie GitHub. Instrukcja znajduje się
w `BUILD_WITHOUT_LOCAL_PYTHON.md`. Gotowy użytkownik instaluje wyłącznie
`LOK_Launcher_Setup_0.3.0.exe`; Python nie jest wymagany do uruchomienia.
