import os
import sys
import subprocess
import configparser

REPO_BASEPATH = ""
PWFILE_LOCATION = ""
DRY_RUN = False

def is_mounted(path):
    try:
        result = subprocess.run(["mountpoint", "-q", path])
        return result.returncode == 0
    except Exception as e:
        print(f"Error checking '{path}': {e}")
        sys.exit()

def mount(path):

    if DRY_RUN:
        print("* DRY_RUN activated. Not mounting anything.")
        return

    try:
        print(f"* Mounting {path}...")
        result = subprocess.run(["mount", path])
    except Exception as e:
        print(f"Error mounting '{path}': {e}")
        sys.exit(1)

def perform_backup(name, path):

    cmd = [
            "restic",
            "-r", f"{REPO_BASEPATH}/{name}", # repository
            "backup",
            "--tag", name,
            "-p", f"{PWFILE_LOCATION}/{name}.txt", # password file
            "--verbose",
            path,
    ]
    
    print(f"* Backing up {name}...")
    print(f'* Issuing command: `{" ".join(cmd)}`')

    if DRY_RUN:
        print("* DRY_RUN activated, Not backing up anything.")
        return

    try:
        result = subprocess.run(cmd)
    except Exception as e:
        print(f"Error performing backup for {name}: {e}")

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

    # print(dict(config['DEFAULT']))

    return config

def should_mount(config):
    return config['DEFAULT']['mount_repo_basepath'] == "True"


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
