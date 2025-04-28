from git import Repo
import os
import shutil

repo_folder = os.path.abspath(os.path.join(os.getcwd(), ".."))
local_folder = os.path.dirname(__file__)
files_to_preserve = ["my_units.csv", "supports.pkl"]

temp_backup = os.path.join(local_folder, "_temp_protected_backup")
os.makedirs(temp_backup, exist_ok=True)

# Preserve user data files
for fname in files_to_preserve:
    src = os.path.join(local_folder, fname)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(temp_backup, fname))

# Git Operations, overwrite repository
os.chdir("..")
project_path = os.getcwd()
repo = Repo(project_path)
o = repo.remotes.origin
o.pull()

# Add back user data files
for fname in files_to_preserve:
    backup = os.path.join(temp_backup, fname)
    if os.path.exists(backup):
        shutil.copy2(backup, os.path.join(local_folder, fname))

# Cleanup
shutil.rmtree(temp_backup)