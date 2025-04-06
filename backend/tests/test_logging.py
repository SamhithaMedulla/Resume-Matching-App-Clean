import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

logger.debug("🔍 This is a DEBUG log.")
logger.info("✅ This is an INFO log.")
logger.warning("⚠️ This is a WARNING log.")
logger.error("❌ This is an ERROR log.")
logger.critical("🔥 This is a CRITICAL log.")
