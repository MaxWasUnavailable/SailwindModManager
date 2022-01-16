from src.Logger.Logger import Logger


class Loggable:
    """
    Class representing anything that can use a logger / be logged.
    Other classes should inherit from this class to make use of the logging functionality.
    """
    def __init__(self, logger: Logger):
        super(Loggable, self).__init__()
        self.logger = None
        self.verbose = False

        if logger is not None:
            logger.register(self)

    def register_logger(self, logger: Logger, verbose: bool) -> None:
        """
        Register a logger to this loggable object.
        :param logger: Logger to connect to.
        :param verbose: Whether or not to enable verbose mode.
        """
        self.logger = logger
        self.verbose = verbose
        self.log(f"Registered to logger {id(self.logger)}.", is_verbose=True)

    def log(self, message: str, is_error: bool = False, is_verbose: bool = False, tags: list = None) -> None:
        """
        Log a message.
        :param message: Message string to log.
        :param is_error: Whether or not the log is an error.
        :param is_verbose: Whether or not to only log this in verbose mode.
        :param tags: What tags to prepend to the log's entry.
        """
        if self.logger is None:
            print(message)
            return

        tags = tags or []
        tags = [id(self)] + tags

        if is_verbose and not self.verbose:
            return
        self.logger.log(message, is_error, is_verbose, tags)
