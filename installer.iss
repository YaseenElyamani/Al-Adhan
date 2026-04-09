; -----------------------------------------------------------------------------
; Al-Adhan Installer
; Build with: right-click installer.iss -> Compile, or run "iscc installer.iss"
; Output: Output\Al-AdhanSetup.exe
; -----------------------------------------------------------------------------

#define MyAppName "Al-Adhan"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Yasee"
#define MyAppExeName "Al-Adhan.exe"

[Setup]
; A unique GUID identifies this app to Windows. Don't change it across
; versions or upgrades will install side-by-side instead of replacing.
; If you ever need a new one, generate via Tools -> Generate GUID in the
; Inno Setup IDE, or https://www.guidgen.com/.
AppId={{7F3C9D2A-4E18-4B6F-9A8C-1D2E3F4A5B6C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename=Al-AdhanSetup
SetupIconFile=images\logo.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; Install for the current user only — no admin prompt required.
; If you ever want a system-wide install (Program Files for all users),
; change this to "admin" and DefaultDirName to "{commonpf}\{#MyAppName}".
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional shortcuts:"
Name: "startupicon"; Description: "Launch {#MyAppName} when Windows starts"; GroupDescription: "Startup options:"

[Files]
; Copy everything PyInstaller produced. The * + recursesubdirs flags pull in
; the _internal/ folder (PyInstaller 6.x) and any other generated files.
Source: "dist\Al-Adhan\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up the per-user data folder on uninstall. Comment this out if you
; want users' saved location to persist across reinstalls.
Type: filesandordirs; Name: "{userappdata}\Al-Adhan"
