import json
import subprocess
import pathlib
import sys
import re

# ==============================
# Console Colors
# ==============================
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\x1b[35m"


def log_step(msg):
    print(f"{C.CYAN}[STEP]{C.RESET} {msg}")


def log_apk(msg):
    print(f"{C.MAGENTA}[APK]{C.RESET} {msg}")


def log_command(msg):
    print(f"{C.BLUE}[COMMAND]{C.RESET} {msg}")


def log_warn(msg):
    print(f"{C.YELLOW}[WARN]{C.RESET} {msg}")


def log_error(msg):
    print(f"{C.RED}[ERROR]{C.RESET} {msg}")


def log_success(msg):
    print(f"{C.GREEN}[OK]{C.RESET} {msg}")

# ==============================
# Paths
# ==============================
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
    #log_command(f"{full_cmd}")

    if capture:
        return subprocess.check_output(full_cmd, shell=True).decode().strip()

    result = subprocess.run(full_cmd, shell=True)
    return result.returncode == 0


def run_raw(cmd: str, capture=False):
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

    if not lines:
        log_error("No connected devices found.")
        sys.exit(1)

    if len(devices) == 1:
        ADB_DEVICE_ARG = f"-s {devices[0]}"
        return

    print(f"{C.BOLD}Multiple devices detected:{C.RESET}")
    for i, d in enumerate(devices):
        print(f"[{i}] {d}")

    idx = int(input("Select device number: "))
    ADB_DEVICE_ARG = f"-s {devices[idx]}"


def install_apk(apk_path, flags):
    success = run(f'install {flags} "{apk_path}"')
    return success


def apply_appops(package, ops):
    for op in ops:
        log_step(f"Executing: {op}")
        run(f"shell appops set --user current {package} {op}")


def apply_pm_grants(package, grants):
    for perm in grants:
        log_step(f"Executing: {perm}")
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


def draw_progress(current, total, bar_length=40):
    percent = current / total
    filled = int(bar_length * percent)
    bar = "█" * filled + "-" * (bar_length - filled)
    sys.stdout.write(f"\r{C.BOLD}Progress:{C.RESET} |{C.GREEN}{bar}{C.RESET}| {current}/{total} ({int(percent*100)}%)")
    sys.stdout.flush()


def select_mode():
    print()
    print(f"{C.BOLD}----------------------------------------{C.RESET}")
    print(f"{C.BOLD}Select mode{C.RESET}")
    print(f"{C.BOLD}----------------------------------------{C.RESET}")
    print()
    print(f"[1] Install (install APKs + apply permissions)")
    print(f"[2] Apply permissions only (skip APK installation)")
    print(f"[3] Exit")
    
    choice = input(f"\n{C.CYAN}Enter your choice (1 or 2): {C.RESET}")
    
    if choice == "1":
        return "install"
    elif choice == "2":
        return "apply_permissions"
    elif choice == "3":
        sys.exit(0)
    else:
        log_error("Invalid choice. Please enter 1, 2, or 3.")
        sys.exit(1)


def apply_permissions_to_package(package, config):
    apply_appops(package, config.get("appops", []))
    apply_pm_grants(package, config.get("pm_grants", []))
    
    if config.get("deviceidle_whitelist", False):
        log_step("Adding to deviceidle whitelist")
        add_deviceidle_whitelist(package)
    
    acc = config.get("accessibility_services", [])
    if acc:
        log_step("Adding accessibility service")
        enable_accessibility_services(acc)


def mode_install(permissions_map):
    """Mode 1: Install APKs and apply permissions"""
    apks = list(APK_DIR.glob("*.apk"))

    if not apks:
        log_warn("No APK files found in apk/ folder.")
        return

    total = len(apks)
    skipped = []
    processed = 0

    print()
    print(f"{C.BOLD}----------------------------------------{C.RESET}")
    print(f"{C.BOLD}Starting installation of {total} APK(s)...{C.RESET}")
    print(f"{C.BOLD}----------------------------------------{C.RESET}")

    for apk_path in apks:
        if processed > 0:
            print()  # move to next line before processing next APK

        processed += 1
        apk_name = apk_path.name

        print()
        log_apk(f"{C.BOLD}{apk_name}{C.RESET}")

        logical_name, config = find_permissions_for_apk(
            apk_name,
            permissions_map
        )

        if not config:
            log_warn(f"No permissions config found. Skipping...")
            skipped.append(f"{C.BOLD}{apk_name}{C.RESET}")
            draw_progress(processed, total)
            continue

        flags = config.get("install_flags", "-r -g")
        package = config["package"]

        success = install_apk(apk_path, flags)
        if not success:
            log_error("Installation failed")
            skipped.append(f"{C.BOLD}{logical_name}{C.RESET} ({apk_name})")
            draw_progress(processed, total)
            continue

        apply_permissions_to_package(package, config)
        draw_progress(processed, total)

    print()  # move to next line after progress bar

    print()
    print(f"{C.BOLD}----------------------------------------{C.RESET}")
    print(f"{C.BOLD}Summary{C.RESET}")
    print(f"{C.BOLD}----------------------------------------{C.RESET}")
    print()

    if skipped:
        log_warn("Skipped APKs:")
        for apk_name in skipped:
            print(f"  - {apk_name}")
    else:
        log_success("All APKs processed successfully")

    print()
    print(f"{C.BOLD}{C.GREEN}Done ✔{C.RESET}")


def mode_apply_permissions(permissions_map):
    total = len(permissions_map)
    processed = 0
    skipped = []

    print()
    print(f"{C.BOLD}----------------------------------------{C.RESET}")
    print(f"{C.BOLD}Applying permissions to {total} package(s)...{C.RESET}")
    print(f"{C.BOLD}----------------------------------------{C.RESET}")

    for logical_name, config in permissions_map.items():
        if processed > 0:
            print()

        processed += 1
        package = config.get("package")

        print()

        if not package:
            log_apk(f"{C.BOLD}{logical_name}{C.RESET}")
            log_warn(f"No package defined for {logical_name}. Skipping...")
            skipped.append(logical_name)
            draw_progress(processed, total)
            continue

        log_apk(f"{C.BOLD}{logical_name}{C.RESET} ({package})")

        # Check if there are any permissions to apply
        has_permissions = (
            config.get("appops", []) or
            config.get("pm_grants", []) or
            config.get("deviceidle_whitelist", False) or
            config.get("accessibility_services", [])
        )

        if not has_permissions:
            log_warn(f"No permissions defined. Skipping...")
            skipped.append(f"{C.BOLD}{logical_name}{C.RESET} ({package})")
            draw_progress(processed, total)
            continue

        try:
            apply_permissions_to_package(package, config)
            draw_progress(processed, total)
        except Exception as e:
            log_error(f"Failed to apply permissions: {e}")
            skipped.append(f"{C.BOLD}{logical_name}{C.RESET} ({package})")
            draw_progress(processed, total)

    print()  # move to next line after progress bar

    print()
    print(f"{C.BOLD}----------------------------------------{C.RESET}")
    print(f"{C.BOLD}Summary{C.RESET}")
    print(f"{C.BOLD}----------------------------------------{C.RESET}")
    print()

    if skipped:
        log_warn("Skipped packages:")
        for package in skipped:
            print(f"  - {package}")
    else:
        log_success("Permissions applied to all packages successfully")

    print()
    print(f"{C.BOLD}{C.GREEN}Done ✔{C.RESET}")

# ==============================
# Main
# ==============================
def main():
    if not APK_DIR.exists():
        log_error("apk folder not found. Create ./apk and put APK files there.")
        return

    if not PERMISSIONS_FILE.exists():
        log_error("permissions.json not found.")
        return

    check_adb()
    select_device()

    # Select operation mode
    mode = select_mode()

    with open(PERMISSIONS_FILE, "r", encoding="utf-8") as f:
        permissions_map = json.load(f)

    if mode == "install":
        mode_install(permissions_map)
    elif mode == "apply_permissions":
        mode_apply_permissions(permissions_map)

if __name__ == "__main__":
    main()