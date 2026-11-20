#define MyAppName "LOK Launcher"
#define MyAppVersion "0.3.0"
#define MyAppPublisher "LOK Launcher"
#define MyAppExeName "LOK Launcher.exe"

[Setup]
AppId={{A2F2B56D-57E0-4A1E-93D0-10C0A0300001}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\LOK Launcher
DefaultGroupName=LOK Launcher
OutputDir=installer_output
OutputBaseFilename=LOK_Launcher_Setup_0.3.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\{#MyAppExeName}
; The uninstaller must never remove the user's .minecraft directory.

[Tasks]
Name: "desktopicon"; Description: "Utwórz ikonę na pulpicie"; GroupDescription: "Dodatkowe skróty:"

[Files]
; Build the app first using build_windows.bat.
Source: "dist\LOK Launcher\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\LOK Launcher"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\LOK Launcher"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Uruchom LOK Launcher"; Flags: postinstall nowait skipifsilent
