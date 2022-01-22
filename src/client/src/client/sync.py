import os
import time

from .. import config


def sync_dir(client, all=False):
    last_sync_path = os.path.join(config.PATH_DATA, ".last_sync")
    if os.path.exists(last_sync_path):
        with open(last_sync_path) as f:
            last_sync = float(f.read())
    else:
        last_sync = 0
    for root, dirs, files in os.walk(config.PATH_PC):
        for file in files:
            print(file)
            filepath = os.path.join(root, file)
            last_modified = os.path.getmtime(filepath)
            new_filepath = filepath.replace(config.PATH_PC, config.PATH_PI)
            new_filepath = new_filepath.replace("\\", "/")
            if last_modified > last_sync or all:
                client.put(filepath, new_filepath)

    os.makedirs(config.PATH_DATA, exist_ok=True)
    with open(last_sync_path, "w") as f:
        f.write(str(time.time()))
