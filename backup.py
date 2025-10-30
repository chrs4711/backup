import os
import sys
import subprocess
import configparser
import urllib.request

REPO_BASEPATH = ""
PWFILE_LOCATION = ""
DRY_RUN = False
RESTIC_BINARY = "/usr/bin/restic"
VERION = "1.2.1"


def is_mounted(path):
    try:
        result = subprocess.run(["mountpoint", "-q", path])
        return result.returncode == 0
    except Exception as e:
        print(f"Error checking '{path}': {e}")
        sys.exit(1)


def perform_backup(name, path):
    cmd = [
        RESTIC_BINARY,
        "-r", f"{REPO_BASEPATH}/{name}",  # repository
        "backup",
        "--tag", name,
        "-p", f"{PWFILE_LOCATION}/{name}.txt",  # password file
        "--verbose",
        path,
    ]

    run_or_die_trying(cmd, f"Backing up {name}")


def forget(name):
    cmd = [
        RESTIC_BINARY,
        "-r", f"{REPO_BASEPATH}/{name}",  # repository
        "-p", f"{PWFILE_LOCATION}/{name}.txt",  # password file
        "forget",
        "--keep-within-daily", "10y"  # --keep-within-daily 10y
    ]

    run_or_die_trying(cmd, f"Forgetting snapshots for {name}")

def set_me_up():
    """
    Checks arguments, processes the config file and sets global parameters/switches.
    Returns the config object
    """

    if len(sys.argv) < 2:
        print("Usage: script <config file> [--dry-run]")
        sys.exit(1)

    config_path = sys.argv[1]

    if not os.path.exists(config_path):
        print(f"Error: Config file `{config_path}` not found.")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(config_path)

    # set some global stuff
    global REPO_BASEPATH
    global PWFILE_LOCATION
    global DRY_RUN

    REPO_BASEPATH = config['DEFAULT']['repo_basepath']
    PWFILE_LOCATION = config['DEFAULT']['pwfile_location']

    if "--dry-run" in sys.argv:
        DRY_RUN = True
        print("!! Dry run activated !!")

    return config


def should_mount(config):
    return config['DEFAULT']['mount_repo_basepath'] == "True"


def report_success(url):
    if DRY_RUN:
        print(f"* DRY_RUN activated, not reporting to {url}")
        return

    print("reporting success")
    urllib.request.urlopen(url)


def mount(path):
    run_or_die_trying(["mount", path], f"Mounting {path}")


def unmount(path):
    run_or_die_trying(["umount", path], f"Umounting {path}")


def run_or_die_trying(cmd, desc):
    print(f"* {desc}...")
    print(f'* [ {" ".join(cmd)} ]')

    if DRY_RUN:
        return

    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f" ERROR {desc}: {e}")
        sys.exit(1)


if __name__ == "__main__":

    config = set_me_up()

    if should_mount(config) and not is_mounted(REPO_BASEPATH):
        mount(REPO_BASEPATH)

    for section in config.sections():
        if section == "DEFAULT":
            continue

        path = config[section]["path"]
        name = config[section]["name"]
        perform_backup(name, path)

        if config[section]["forget"] == "True":
            forget(name)

    if is_mounted(REPO_BASEPATH):
        unmount(REPO_BASEPATH)

    report_success(config['DEFAULT']['heartbeat_url'])
