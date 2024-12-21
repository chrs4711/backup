import os
import sys
import subprocess

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

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: script <repo basepath>")
        sys.exit(1)

    repo_basepath = sys.argv[1]
    print(f"repo location: {repo_basepath}")

    # if not is_mounted(BACKUP_LOCATION):
    #    mount(BACKUP_LOCATION)

    perform_backup("/mnt/storage/share/Documents", repo_basepath, "documents")
    # perform_backup("/mnt/foobar", "foobar")
