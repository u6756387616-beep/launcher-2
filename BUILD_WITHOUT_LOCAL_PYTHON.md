# Jak dostać gotowy instalator bez instalowania Pythona na swoim komputerze

Ważne: ZIP z kodem źródłowym nie jest jeszcze gotowym instalatorem. Python jest
potrzebny maszynie budującej program, ale nie komputerowi, na którym będzie
uruchamiany gotowy LOK Launcher.

## Najprostsza metoda: budowanie przez GitHub Actions

1. Zaloguj się na GitHub i utwórz nowe, prywatne repozytorium.
2. Wgraj do niego całą zawartość tego folderu ZIP (w tym folder `.github`).
3. Otwórz repozytorium → zakładka **Actions**.
4. Wybierz workflow **Build LOK Launcher for Windows**.
5. Kliknij **Run workflow** i poczekaj na zakończenie budowania.
6. Otwórz zakończony przebieg workflow i pobierz artifact
   `LOK-Launcher-Windows-Installer`.
7. W środku będzie `LOK_Launcher_Setup_0.3.0.exe`.

Gotowy instalator jest samodzielny: użytkownik nie musi instalować Pythona.
Do samego uruchamiania Minecrafta nadal potrzebne są pliki gry, Java/runtime
odpowiedni dla wersji oraz legalne logowanie Microsoft (integracja OAuth jest
osobnym etapem projektu).

## Budowanie lokalne

Jeżeli masz komputer deweloperski z Windows, możesz uruchomić
`build_windows.bat`. Python i Inno Setup są wtedy potrzebne wyłącznie do
zbudowania instalatora, a nie do korzystania z gotowego programu.
