import os
import time

from .config import Config


def sync_dir(client, all=False):
    last_sync_path = os.path.join(Config.PATH_DATA, ".last_sync")
    if os.path.exists(last_sync_path):
        with open(last_sync_path) as f:
            last_sync = float(f.read())
    else:
        last_sync = 0
    synced_count = 0
    path_src = Config.PATH_PC if Config.USE_PC else Config.PATH_LAPTOP
    for root, dirs, files in os.walk(path_src):
        for file in files:
            filepath = os.path.join(root, file)
            last_modified = os.path.getmtime(filepath)
            new_filepath = filepath.replace(path_src, Config.PATH_PI)
            new_filepath = new_filepath.replace("\\", "/")
            if last_modified > last_sync or all:
                client.put(filepath, new_filepath)
                synced_count += 1

    os.makedirs(Config.PATH_DATA, exist_ok=True)
    with open(last_sync_path, "w") as f:
        f.write(str(time.time()))

    return synced_count
