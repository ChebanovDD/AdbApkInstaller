# AdbApkInstaller
# APK Deploy Tool (ADB Auto Installer)

---

## 🚀 Overview

This tool automates:

- Installing multiple APK files via ADB
- Applying required permissions automatically
- Applying AppOps permissions
- Adding apps to Device Idle whitelist
- Adding Accessibility services (without overwriting existing ones)
- Selecting target device if multiple devices are connected
- Fuzzy matching APK filenames to permission configs
- Skipping unknown APKs and reporting them
- Showing install progress (how many APKs left)

---

## ✨ Features

### 📦 APK Installation
- Installs all APK files located inside **apk/** folder next to the script
- Supports install flags per app

### 🔐 Permissions Automation
Supports:
- pm grant
- appops set
- accessibility services merge-safe enable
- deviceidle whitelist

### 🧠 Smart Config Matching
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

### 📱 Multi-Device Support
If multiple devices connected → user selects target device.

### 📊 Progress Display
Shows:

```
[2 / 5] Installing gm_floating_menu.apk
```

### ⚠️ Skip Reporting
Shows list of APKs without config at end.

---

## 📂 Folder Structure

```
deploy_apk/
 ├ install_apks.py
 ├ permissions.json
 ├ apk/
 │   ├ app1.apk
 │   ├ app2.apk
 │   └ app3.apk
```

---

# 🧩 permissions.json Format

```
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

---

# 🧑‍💻 Installation Guide

---

# ✅ STEP 1 — Check Python Installation

## Windows

Open PowerShell:

```
python --version
```

OR

```
py --version
```

If installed → shows version.

---

## Install Python (Windows)

1. Go to:

```
https://www.python.org/downloads/
```

2. Download latest Python
3. IMPORTANT:

✔ Check **Add Python to PATH**

4. Click Install

---

## Mac

Open Terminal:

```
python3 --version
```

If not installed:

```
brew install python
```

If Homebrew missing:

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

# ✅ STEP 2 — Check ADB Installation

## Windows

```
adb version
```

If missing:

### Install Android Platform Tools

1. Download:

```
https://developer.android.com/studio/releases/platform-tools
```

2. Extract to:

```
C:\\platform-tools
```

3. Add to PATH

System → Environment Variables → PATH → Add:

```
C:\\platform-tools
```

Restart terminal.

---

## Mac

```
brew install android-platform-tools
```

Check:

```
adb version
```

---

# ✅ STEP 3 — Check Device Connection

```
adb devices
```

Should show:

```
List of devices attached
XXXXXXXX device
```

---

# ▶ Running The Tool

```
python install_apks.py
```

OR Mac:

```
python3 install_apks.py
```

---

# 📊 Progress Example

```
Found 4 APKs

[1 / 4] Installing gm_floating_menu.apk
[2 / 4] Installing hud.apk
[3 / 4] Installing overlay.apk
[4 / 4] Installing debugtool.apk
```

---

# 🧠 Matching Logic

Normalization removes:

- underscores
- dashes
- dots
- spaces
- version numbers

---

# ⚠️ Skip Example

```
Skipped APKs:
 - test_build.apk
 - unknown_tool.apk
```

---

# 🎯 Done

You now have a production-grade APK deployment automation tool that loads APKs from a dedicated folder.

---