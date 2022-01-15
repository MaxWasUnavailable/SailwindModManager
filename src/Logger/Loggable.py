from src.Logger.Logger import Logger


class Loggable:
    def __init__(self, logger: Logger):
        super(Loggable, self).__init__()
        self.logger = None
        self.verbose = False

        if logger is not None:
            logger.register(self)

    def register_logger(self, logger, verbose):
        self.logger = logger
        self.verbose = verbose
        self.log(f"Registered to logger {id(self.logger)}.", is_verbose=True)

    def log(self, message: str, is_error: bool = False, is_verbose: bool = False, tags: list = None):
        if self.logger is None:
            print(message)
            return

        tags = tags or []
        tags = [id(self)] + tags

        if is_verbose and not self.verbose:
            return
        self.logger.log(message, is_error, is_verbose, tags)
