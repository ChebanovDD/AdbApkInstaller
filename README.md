# AdbApkInstaller

APK deployment automation tool.

<p align="right">
  <a href="README.md">🇺🇸 English</a> |
  <a href="README.ru.md">🇷🇺 Русский</a>
</p>

## :open_book: Table of Contents

- [Overview](#pencil-overview)
- [Folder Structure](#cactus-folder-structure)
- [Permissions JSON Format](#jigsaw-permissions-json-format)
- [Installation Guide](#gear-installation-guide)
- [How To Use](#rocket-how-to-use)

## :pencil: Overview

This tool automates:

- Installing multiple APK files via ADB
- Applying required permissions automatically
- Applying AppOps permissions
- Adding apps to Device Idle whitelist
- Adding Accessibility services (without overwriting existing ones)
- Selecting target device if multiple devices are connected
- Fuzzy matching APK filenames to permission configs

### APK Installation

- Installs all APK files located inside **apk/** folder next to the script
- Supports install flags per app

### Permissions Automation

Supports:
- pm grant
- appops set
- deviceidle whitelist
- accessibility services merge-safe enable

### Smart Config Matching
Matches logical app names like:

```
GMFloatingMenu
```

With APKs like:

```
gm_floating_menu.apk
gm_floating_menu_v1.2.0.apk
gmfloatingmenu.apk
```

Normalization app names logic removes:

- underscores
- dashes
- dots
- spaces
- version numbers

### Multi-Device Support
If multiple devices connected → user selects target device.

### Skip Reporting
Shows list of APKs without config at end.

## :cactus: Folder Structure

    AdbApkInstaller/
    ├── install_apks.py
    ├── permissions.json
    ├── apk/
    │   ├── app1.apk
    │   ├── app2.apk
    │   └── app3.apk

## :jigsaw: Permissions JSON Format

```json
{
  "GMFloatingMenu": {
    "package": "com.chebanovdd.gmfloatingmenu",
    "install_flags": "-r -g -d",
    "appops": [
      "SYSTEM_ALERT_WINDOW allow"
    ],
    "pm_grants": [
      "android.permission.WRITE_SECURE_SETTINGS"
    ],
    "deviceidle_whitelist": true,
    "accessibility_services": [
      "com.chebanovdd.gmfloatingmenu/.AccessibilityService"
    ]
  }
}
```

## :gear: Installation Guide

### :white_check_mark: STEP 1 — Check Python Installation

#### Windows

Open PowerShell:

```shell
python --version
```

OR

```shell
py --version
```

Shows version if installed. Else download latest [Python](https://www.python.org/downloads/).

> **Note:** Make sure Python is added to PATH.

#### Mac

Open Terminal:

```shell
python3 --version
```

If not installed:

```shell
brew install python
```

If Homebrew missing:

```shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### :white_check_mark: STEP 2 — Check ADB Installation

#### Windows

```shell
adb version
```

If missing:

1. Download [Android Platform Tools](https://developer.android.com/studio/releases/platform-tools)
2. Extract to `C:\\platform-tools`
3. Add to PATH `System → Environment Variables → PATH`
4. Restart terminal

#### Mac

```shell
adb version
```

If missing:

```shell
brew install android-platform-tools
```

### :white_check_mark: STEP 3 — Check Device Connection

```shell
adb devices
```

Should show:

```shell
List of devices attached
XXXXXXXX device
```

## :rocket: How To Use

```shell
python install_apks.py
```

OR Mac:

```shell
python3 install_apks.py
```