import os
import traceback
import logging
import pysftp


class SyncHandler:
    def __init__(self, config):
        self.config = config
        self.last_sync = self.load_last_sync_time()
        self.files_src = self.load_files_src_folder()

    def load_last_sync_time(self):
        try:
            with open(self.config.filepath_last_sync) as f:
                last_sync = float(f.read())
        except FileNotFoundError:
            logging.info("This directory was not synced before. ")
            last_sync = 0
        except:
            traceback.print_exc()

        return last_sync

    def load_files_src_folder(self):
        files_sync = []
        for root, _, files in os.walk(self.config.src_folder):
            for file in files:
                file_path = os.path.join(root, file)
                if self.config.sync_all or os.path.getmtime(file_path) >= self.last_sync or self.last_sync == 0:
                    relative_filepath = file_path[len(self.config.src_folder):]
                    relative_filepath = relative_filepath.lstrip("/")
                    files_sync.append(relative_filepath)
        self.filter_files_sync(files_sync)
        return files_sync

    def _filter_excluded_dirs(self, files_sync):
        for dir in self.config.excluded_dirs:
            if dir.startswith("**"):
                mode = 2
            elif dir.startswith("*"):
                mode = 1
            else:
                mode = 0
            for file in files_sync.copy():
                # relative filepath to src directory

                if (mode == 2 and dir[2:] in file or
                    mode == 1 and dir[1:] in file.split("/") or
                        mode == 0 and file.startswith(dir)):
                    files_sync.remove(file)
                    logging.info(
                        f"'{file}' was excluded because of excluded_dirs")

    def _filter_excluded_files(self, files_sync):
        if self.config.filename_last_sync in files_sync:
            files_sync.remove(self.config.filename_last_sync)
            logging.info(
                f"'{self.config.filepath_last_sync}' was removed")
        for file_type in self.config.excluded_files:
            if file_type.startswith("**"):
                mode = 2
            elif file_type.startswith("*"):
                mode = 1
            else:
                mode = 0
            for file in files_sync.copy():
                if (mode == 2 and file_type[2:] in file or
                    mode == 1 and file_type[1:] == file.split("/")[-1] or
                        mode == 0 and file == file_type):
                    files_sync.remove(file)
                    logging.info(
                        f"'{file}' was excluded because of excluded_files")

    def filter_files_sync(self, files_sync):
        self._filter_excluded_dirs(files_sync)
        self._filter_excluded_files(files_sync)

    def sync(self):
        self.load_last_sync_time()
        self.load_files_src_folder()
        if len(self.files_src) <= 0:
            return
        with pysftp.Connection(self.config.host, username=self.config.username, password=self.config.password, log=False) as sftp:
            logging.info("Connection succesfully stablished ... ")
            if not sftp.exists(self.config.dest_folder):
                sftp.mkdir(self.config.dest_folder)
            sftp.chdir(self.config.dest_folder)
            for file in self.files_src:
                src_path = os.path.join(self.config.src_folder, file)
                dest_dirs = file.split('/')[0:-1]
                dest_dirs_path = ""
                for dest_dir in dest_dirs:
                    dest_dirs_path = os.path.join(dest_dirs_path, dest_dir)
                    if not sftp.exists(dest_dirs_path):
                        sftp.mkdir(dest_dirs_path)
                        logging.info(
                            f"Created directory '{dest_dirs_path}'")
                sftp.put(src_path, file)

    def print_sync_files(self):
        print("Synced: ", end="\n\t")
        print(*self.files_src, sep='\n\t')
