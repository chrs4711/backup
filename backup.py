import os
import sys
import subprocess
import configparser

PWFILE_LOCATION="/etc/restic"


def is_mounted(path):
    try:
        result = subprocess.run(["mountpoint", "-q", path])
        return result.returncode == 0
    except Exception as e:
        print(f"Error checking '{path}': {e}")
        sys.exit()

def mount(path):
    try:
        print(f"Mounting {path}...")
        result = subprocess.run(["mount", path])
    except Exception as e:
        print(f"Error mounting '{path}': {e}")
        sys.exit(1)

def perform_backup(path, repo_basepath, name):

    cmd = [
            "restic",
            "-r", f"{repo_basepath}/{name}", # repository
            "backup",
            "--tag", name,
            "-p", f"{PWFILE_LOCATION}/{name}.txt", # password file
            "--verbose",
            path,
    ]
    
    print(f"Backing up {name}...")
    print(f'Issuing command: `{" ".join(cmd)}`')

    try:
        result = subprocess.run(cmd)
    except Exception as e:
        print(f"Error performing backup for {name}: {e}")

def read_config(config_path):

    if not os.path.exists(config_path):
        print(f"Error: Config file `{config_path}` not found.")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(config_path)

    return config


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: script <repo basepath>")
        sys.exit(1)

    repo_basepath = sys.argv[1]
    print(f"repo basepath is: `{repo_basepath}`")

    config = read_config("config.cfg")

    for section in config.sections():
        path = config[section]["path"]
        name = config[section]["name"]

        print(f'backing up: {name} in {path} to {repo_basepath}/{name}')

    # if not is_mounted(repo_basepath):
    #    mount(repo_basepath)

    # perform_backup("/mnt/storage/share/Documents", repo_basepath, "documents")
    # perform_backup("/mnt/foobar", "foobar")
