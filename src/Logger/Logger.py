from os.path import exists
from os import mkdir
import datetime


class Logger:
    def __init__(self, log_folder: str = "./data/logs", logfile_name: str = None, to_file: bool = True, verbose: bool = True, to_console: bool = True, no_logs: bool = False):
        self.logging_objects = []
        self.log_string = ""
        self.log_folder = log_folder
        self.to_file = to_file
        self.verbose = verbose
        self.to_console = to_console
        self.no_logs = no_logs

        logfile_default_name = str(datetime.datetime.now().replace(microsecond=0)).replace(":", "-").replace(" ", "_")
        self.logfile_name = logfile_name or f"{logfile_default_name}.log"

        self.clear_file()
        self.log(f"Logger {id(self)} initialised.")

    def register(self, obj):
        self.logging_objects.append(obj)
        obj.register_logger(self, self.verbose)

    def log(self, message: str, is_error: bool = False, is_verbose: bool = False, tags: list = None):
        if self.no_logs:
            return

        tags = tags or []
        tags_string = ""
        for tag in tags:
            tags_string += f"[{str(tag)}]"

        if is_verbose and not self.verbose:
            return

        if is_error:
            message = f"[{datetime.datetime.now().time()}][ERROR]{tags_string} {message}"
        else:
            message = f"[{datetime.datetime.now().time()}]{tags_string} {message}"

        self.log_string += message + "\n"

        if self.to_file:
            self.append_to_file(message)

        if self.to_console:
            print(message)

    def clear_file(self):
        self.__check_dir()
        open(f"{self.log_folder}/{self.logfile_name}", 'w').close()

    def append_to_file(self, message: str):
        self.__check_dir()
        with open(f"{self.log_folder}/{self.logfile_name}", 'a') as file:
            file.write(message + "\n")
            file.close()

    def __check_dir(self, create_if_not_exist: bool = True):
        if not exists(self.log_folder):
            if not create_if_not_exist:
                return False
            mkdir(self.log_folder)
        return True
