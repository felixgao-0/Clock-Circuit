# A file for debugging and stuff
class LoggerConfigException(Exception):
    pass

class base_logger:
    def __init__(self, *, level="WARNING"):
        if level not in [None, "DEBUG", "INFO", "WARNING", "ERROR"]:
            raise LoggerConfigException("Invalid Level")
        self.level = level

    def debug(self, message):
        if self.level in ["DEBUG"]:
            print(f"DEBUG:   {message}")

    def info(self, message):
        if self.level in ["DEBUG", "INFO"]:
            print(f"INFO:    {message}")

    def warning(self, message):
        if self.level in ["DEBUG", "INFO", "WARNING"]:
            print(f"WARNING: {message}")

    def error(self, message):
        if self.level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            print(f"ERROR:   {message}")
