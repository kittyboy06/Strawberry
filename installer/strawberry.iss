; 🍓 Strawberry Inno Setup Script
; Generates: Strawberry_Setup.exe
; Installs per-user, registers PATH, and configures background sync daemon by default.

#define MyAppName "Strawberry"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Strawberry Team"
#define MyAppURL "https://github.com/Kittyboy06/Strawberry"
#define MyAppExeName "strawberry.exe"

[Setup]
AppId={{9F56A493-2720-41C2-8224-817B6D97D9B9}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\Strawberry
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Lowest privileges required (Per-user install, no administrator UAC prompt)
PrivilegesRequired=lowest
OutputDir=..\dist
OutputBaseFilename=Strawberry_Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ChangesEnvironment=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Standalone Windows Executable
Source: "..\strawberry-cli\dist\{#MyAppExeName}"; DestDir: "{app}\bin"; Flags: ignoreversion
; Documentation & License
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\docs\architecture.md"; DestDir: "{app}\docs"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\bin\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\bin\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; 1. Automatically register background sync daemon in Windows Startup by default
Filename: "{app}\bin\{#MyAppExeName}"; Parameters: "install-startup"; Flags: runhidden
; 2. Automatically launch the background sync daemon immediately
Filename: "{app}\bin\{#MyAppExeName}"; Parameters: "daemon"; Flags: nowait runhidden

[UninstallRun]
; Terminate active Strawberry daemon process cleanly upon uninstall
Filename: "taskkill.exe"; Parameters: "/f /im {#MyAppExeName}"; Flags: runhidden

[UninstallDelete]
; Clean up Startup entry and cache
Type: files; Name: "{userstartup}\StrawberryDaemon.vbs"
Type: filesandordirs; Name: "{app}\cache"
Type: files; Name: "{app}\catalog.db"
Type: files; Name: "{app}\sync_state.json"

[Code]
// ─────────────────────────────────────────────────────────────────────────────
// Windows User PATH Environment Variable Registration
// ─────────────────────────────────────────────────────────────────────────────

const
  EnvironmentKey = 'Environment';

function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, EnvironmentKey, 'Path', OrigPath) then
  begin
    Result := True;
    exit;
  end;
  // Look for the directory in Path
  Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  BinDir: string;
  OldPath: string;
  NewPath: string;
begin
  if CurStep = ssPostInstall then
  begin
    BinDir := ExpandConstant('{app}\bin');
    if RegQueryStringValue(HKEY_CURRENT_USER, EnvironmentKey, 'Path', OldPath) then
    begin
      if NeedsAddPath(BinDir) then
      begin
        if (Length(OldPath) > 0) and (OldPath[Length(OldPath)] <> ';') then
          OldPath := OldPath + ';';
        NewPath := OldPath + BinDir;
        RegWriteStringValue(HKEY_CURRENT_USER, EnvironmentKey, 'Path', NewPath);
      end;
    end
    else
    begin
      RegWriteStringValue(HKEY_CURRENT_USER, EnvironmentKey, 'Path', BinDir);
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  BinDir: string;
  OldPath: string;
  NewPath: string;
  P: Integer;
begin
  if CurUninstallStep = usUninstall then
  begin
    BinDir := ExpandConstant('{app}\bin');
    if RegQueryStringValue(HKEY_CURRENT_USER, EnvironmentKey, 'Path', OldPath) then
    begin
      P := Pos(BinDir, OldPath);
      if P > 0 then
      begin
        // Remove path and semicolon
        Delete(OldPath, P, Length(BinDir));
        OldPath := StringChange(OldPath, ';;', ';');
        RegWriteStringValue(HKEY_CURRENT_USER, EnvironmentKey, 'Path', OldPath);
      end;
    end;
  end;
end;
