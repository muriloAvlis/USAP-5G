from loguru import logger
import sys
import os


class Log:
    _logger = None

    @classmethod
    def configure(cls):
        """Configura o logger global para o projeto."""

        logLevel = os.getenv("LOG_LEVEL", "INFO")

        if cls._logger is None:
            logger.remove()  # Remove os handlers padrões do loguru
            logger.add(
                sys.stdout,
                format="[<green>{time:YYYY-MM-DD HH:mm:ss}</green>] "
                       "[<level>{level}</level>] "
                       "[<cyan>{file}</cyan>:<cyan>{line}</cyan>] "
                       "<level>{message}</level>",
                level=logLevel,
                colorize=True
            )
            # Adicione outros destinos, como arquivos, se necessário
            logger.add(
                "/tmp/usap_smc.log",
                rotation="5 MB",
                retention="7 days",
                level="INFO",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {module}:{function}:{line} - {message}"
            )
