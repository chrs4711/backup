import os
import sys
import subprocess

BACKUPREPO_LOCATION="/mnt/nextcloud-backup"
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
        sys.exit()

def perform_backup(path, name):

    cmd = [
            "restic",
            "-r", f"{BACKUPREPO_LOCATION}/{name}", # repository
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

    # if not is_mounted(BACKUP_LOCATION):
    #    mount(BACKUP_LOCATION)

    perform_backup("/mnt/storage/share/Documents", "documents")
    # perform_backup("/mnt/foobar", "foobar")
