from sync_handler import SyncHandler
import logging
from config import Config

config = Config()
if config.logging_file:
    logging.basicConfig(filename='sync.log',
                        filemode='w',
                        level=config.logging_level,
                        format='%(levelname)s: %(message)s')
else:
    logging.basicConfig(level=config.logging_level,
                        format='%(levelname)s: %(message)s')

sync_handler = SyncHandler(config)
sync_handler.sync()
sync_handler.print_sync_files()
