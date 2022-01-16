from os.path import exists
from os import mkdir
import datetime


class Logger:
    """
    Represents a logger.
    Logs log messages to console and/or a log file.
    Loggable objects register with the logger to get connected to it and make use of it.
    """
    def __init__(self, log_folder: str = "./data/logs", logfile_name: str = None, to_file: bool = True, verbose: bool = True, to_console: bool = True, no_logs: bool = False):
        """
        :param log_folder: What folder to write new logs to
        :param logfile_name: Name of the log's file. Can be used to ensure only a single log file is ever used. (For example for debugging)
        :param to_file: Whether or not to write logs to a file
        :param verbose: Whether or not to log verbose messages
        :param to_console: Whether or not to output to the console
        :param no_logs: Whether or not to disable logging entirely
        """
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

    def register(self, obj) -> None:
        """
        Registers an object that inherits from Loggable to the Logger, and vice versa.
        :param obj: Object that inherits from Loggable class that will be registered
        """
        self.logging_objects.append(obj)
        obj.register_logger(self, self.verbose)

    def log(self, message: str, is_error: bool = False, is_verbose: bool = False, tags: list = None) -> None:
        """
        Log a message.
        :param message: Message string to log.
        :param is_error: Whether or not the log is an error.
        :param is_verbose: Whether or not to only log this in verbose mode.
        :param tags: What tags to prepend to the log's entry.
        """
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

    def clear_file(self) -> None:
        """
        Clear (or create) the log file.
        """
        self.__check_dir()
        open(f"{self.log_folder}/{self.logfile_name}", 'w').close()

    def append_to_file(self, message: str) -> None:
        """
        Append a string to the log file.
        :param message: Message string to append to file.
        """
        self.__check_dir()
        with open(f"{self.log_folder}/{self.logfile_name}", 'a') as file:
            file.write(message + "\n")
            file.close()

    def __check_dir(self, create_if_not_exist: bool = True) -> bool:
        """
        Checks if the log directory exists, and optionally creates it.
        :param create_if_not_exist: Whether or not to create the directory if it doesn't exist.
        :return: boolean to indicate whether or not the directory exists.
        """
        if not exists(self.log_folder):
            if not create_if_not_exist:
                return False
            mkdir(self.log_folder)
        return True
