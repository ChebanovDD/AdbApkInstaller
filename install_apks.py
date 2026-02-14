import json
import subprocess
import pathlib
import re

SCRIPT_DIR = pathlib.Path(__file__).parent
APK_DIR = SCRIPT_DIR / "apk"
PERMISSIONS_FILE = SCRIPT_DIR / "permissions.json"
ADB_DEVICE_ARG = ""


def normalize_name(name: str):
    name = name.lower()
    name = re.sub(r'[\s_\-\.]', '', name)
    name = re.sub(r'v?\d+(\.\d+)*', '', name)
    return name


def find_permissions_for_apk(apk_name, permissions_map):
    apk_norm = normalize_name(apk_name.replace(".apk", ""))

    for logical_name, data in permissions_map.items():
        logical_norm = normalize_name(logical_name)
        if logical_norm in apk_norm or apk_norm in logical_norm:
            return logical_name, data

    return None, None


def run(cmd: str, capture=False):
    full_cmd = f"adb {ADB_DEVICE_ARG} {cmd}"
    print(f"\n>>> {full_cmd}")

    if capture:
        return subprocess.check_output(full_cmd, shell=True).decode().strip()

    result = subprocess.run(full_cmd, shell=True)
    if result.returncode != 0:
        raise RuntimeError(full_cmd)


def run_raw(cmd: str, capture=False):
    print(f"\n>>> {cmd}")

    if capture:
        return subprocess.check_output(cmd, shell=True).decode().strip()

    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        raise RuntimeError(cmd)


def check_adb():
    run_raw("adb version")


def select_device():
    global ADB_DEVICE_ARG

    out = run_raw("adb devices", capture=True)
    lines = out.split("\n")[1:]

    devices = [l.split()[0] for l in lines if "device" in l]

    if len(devices) == 1:
        ADB_DEVICE_ARG = f"-s {devices[0]}"
        return

    print("Multiple devices:")
    for i, d in enumerate(devices):
        print(f"[{i}] {d}")

    idx = int(input("Select device: "))
    ADB_DEVICE_ARG = f"-s {devices[idx]}"


def install_apk(apk_path, flags):
    run(f'install {flags} "{apk_path}"')


def apply_appops(package, ops):
    for op in ops:
        run(f"shell appops set --user current {package} {op}")


def apply_pm_grants(package, grants):
    for perm in grants:
        run(f"shell pm grant --user current {package} {perm}")


def add_deviceidle_whitelist(package):
    run(f"shell dumpsys deviceidle whitelist +{package}")


def get_enabled_accessibility():
    try:
        current = run(
            "shell settings get secure enabled_accessibility_services",
            capture=True
        )
        if current == "null":
            return []
        return current.split(":")
    except:
        return []


def set_enabled_accessibility(services):
    joined = ":".join(services)
    run(f'shell settings put secure enabled_accessibility_services "{joined}"')


def enable_accessibility_services(new_services):
    current = get_enabled_accessibility()
    updated = list(current)

    for s in new_services:
        if s not in updated:
            updated.append(s)

    set_enabled_accessibility(updated)
    run("shell settings put secure accessibility_enabled 1")


def main():
    check_adb()
    select_device()

    if not APK_DIR.exists():
        print("apk folder not found. Create ./apk and put APK files there.")
        return

    with open(PERMISSIONS_FILE, "r", encoding="utf-8") as f:
        permissions_map = json.load(f)

    apks = list(APK_DIR.glob("*.apk"))
    skipped = []

    total = len(apks)
    processed = 0

    print(f"Found {total} APKs in apk/ folder")

    for apk_path in apks:
        processed += 1
        apk_name = apk_path.name

        print(f"\n[{processed} / {total}] Installing {apk_name}")

        logical_name, config = find_permissions_for_apk(
            apk_name,
            permissions_map
        )

        if not config:
            skipped.append(apk_name)
            print("No config found → skipped")
            continue

        flags = config.get("install_flags", "-r -g")
        package = config["package"]

        install_apk(apk_path, flags)
        apply_appops(package, config.get("appops", []))
        apply_pm_grants(package, config.get("pm_grants", []))

        if config.get("deviceidle_whitelist", False):
            add_deviceidle_whitelist(package)

        acc = config.get("accessibility_services", [])
        if acc:
            enable_accessibility_services(acc)

    if skipped:
        print("\nSkipped APKs:")
        for s in skipped:
            print(" -", s)


if __name__ == "__main__":
    main()