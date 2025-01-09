from datetime import datetime, timezone
from mdclogpy import Logger, Level


class Log(Logger):
    def __init__(self, name: str = 'usap-xapp', level: Level = Level.INFO):
        super().__init__(name, level)

    def get_current_datetime(self):
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    def error(self, message: str):
        """Log an error message. Equals to log(ERROR, msg)."""
        self.add_mdc('time', self.get_current_datetime())
        self.log(Level.ERROR, message)

    def warning(self, message: str):
        """Log a warning message. Equals to log(WARNING, msg)."""
        self.add_mdc('time', self.get_current_datetime())
        self.log(Level.WARNING, message)

    def info(self, message: str):
        """Log an info message. Equals to log(INFO, msg)."""
        self.add_mdc('time', self.get_current_datetime())
        self.log(Level.INFO, message)

    def debug(self, message: str):
        """Log a debug message. Equals to log(DEBUG, msg)."""
        self.add_mdc('time', self.get_current_datetime())
        self.log(Level.DEBUG, message)
