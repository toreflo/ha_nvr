"""
 This file implements service media_dir.clear. It is intended to keep target directory size below target size.
 If current size is bigger, service media_dir.clear starts deleting subdirectories one by one in alphabetical order
 until size gets below the target. So, using subdirectory names like YYYYDDMM, older subdirectories are deleted first.
"""

import os
import time
import shutil
import logging

ATTR_FOLDER = "folder"
ATTR_SIZE = "size"

SERVICE_NAME = "clear"

DEFAULT_FOLDER = "/this/folder/does/not/exists/"
DEFAULT_SIZE = 1000000000

DOMAIN = "media_dir"

_LOGGER = logging.getLogger(__name__)

def setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""
    
    def get_directory_size(directory):
        """Returns the `directory` size in bytes."""
        total = 0
        try:
          # print("[+] Getting the size of", directory)
          for entry in os.scandir(directory):
              if entry.is_file():
                  # if it's a file, use stat() function
                  total += entry.stat().st_size
              elif entry.is_dir():
                  # if it's a directory, recursively call this function
                  total += get_directory_size(entry.path)
        except NotADirectoryError:
          # if `directory` isn't a directory, get the file size then
          return os.path.getsize(directory)
        except PermissionError:
          # if for whatever reason we can't open the folder, return 0
          return 0
        return total

    def remove_dir(dir_path):
        try:
            shutil.rmtree(dir_path)
        except OSError as e:
            _LOGGER.error("Cannot remove folder {}".format(dir_path))
            raise Exception("Cannot remove folder {}".format(dir_path))

    def handle_clear_folder(call):
        """Handle the service call."""
        folder_path = call.data.get(ATTR_FOLDER, DEFAULT_FOLDER)
        folder_size = call.data.get(ATTR_SIZE, DEFAULT_SIZE)
        now = time.time()

        if os.path.isdir(folder_path):
            size = get_directory_size(folder_path)
            while size > folder_size:           
                dir = sorted(os.listdir(folder_path))[0]
                _LOGGER.info("Size is {}, removing dir {}".format(size, dir))
                remove_dir(os.path.join(folder_path, dir))
                size = get_directory_size(folder_path)
        else:
            _LOGGER.error("{} is not recognized as a folder".format(folder_path))
            raise Exception("{} is not recognized as a folder".format(folder_path))
        
    hass.services.register(DOMAIN, SERVICE_NAME, handle_clear_folder)
    # Return boolean to indicate that initialization was successfully.
    return True