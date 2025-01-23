from loguru import logger
from usap_smc.logger.logger import Log

if __name__ == "__main__":
    Log.configure()
    logger.info("Info logger")
    logger.warning("Info logger")
    logger.error("Info logger")
    logger.debug("Info logger")
    logger.success("Info logger")
