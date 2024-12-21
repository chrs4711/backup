import os
import sys
import subprocess
import configparser

REPO_BASEPATH = ""
PWFILE_LOCATION = ""

def is_mounted(path):
    try:
        result = subprocess.run(["mountpoint", "-q", path])
        return result.returncode == 0
    except Exception as e:
        print(f"Error checking '{path}': {e}")
        sys.exit()

def mount(path):
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

    # try:
    #     result = subprocess.run(cmd)
    # except Exception as e:
    #     print(f"Error performing backup for {name}: {e}")

def read_config(config_path):

    if not os.path.exists(config_path):
        print(f"Error: Config file `{config_path}` not found.")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(config_path)

    # set some global stuff
    global REPO_BASEPATH
    global PWFILE_LOCATION
    REPO_BASEPATH = config['DEFAULT']['repo_basepath']
    PWFILE_LOCATION = config['DEFAULT']['pwfile_location']

    return config


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: script <config file>")
        sys.exit(1)

    config_file_path = sys.argv[1]
    config = read_config(config_file_path)

    print(f"* Got configuration: basepath: {REPO_BASEPATH}, pw: {PWFILE_LOCATION}")

    # if not is_mounted(repo_basepath):
    #    mount(repo_basepath)

    for section in config.sections():
        if section == "DEFAULT":
            continue

        path = config[section]["path"]
        name = config[section]["name"]

        perform_backup(name, path)
