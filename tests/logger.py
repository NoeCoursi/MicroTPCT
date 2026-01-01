from microtpct.utils.logging import setup_logger

logger = setup_logger(__name__, log_file="logs/test.log")
print(__name__)

logger.info("Starting alignement step")
logger.warning("Sequence shorter than expected")
logger.error("Alignment failed")