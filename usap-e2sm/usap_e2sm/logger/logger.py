import structlog


class Log(object):
    logger = structlog.getLogger()

    def __init__(self):
        if Log.logger is None:
            logger = structlog.get_logger()

    @staticmethod
    def get_logger():
        return Log.logger
