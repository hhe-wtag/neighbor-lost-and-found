import logging
import logging.config
import os
import time
from typing import Callable
import yaml
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Get the absolute path of THIS file
CURRENT_FILE = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(CURRENT_FILE))

LOG_DIR = os.path.join(BASE_DIR, "logs")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "logging.yaml")

print(f"[DEBUG] Current file: {CURRENT_FILE}")
print(f"[DEBUG] BASE_DIR: {BASE_DIR}")
print(f"[DEBUG] LOG_DIR: {LOG_DIR}")
print(f"[DEBUG] CONFIG_PATH: {CONFIG_PATH}")

# Ensure the log directory exists
os.makedirs(LOG_DIR, exist_ok=True)
print(f"[DEBUG] Created/verified log directory: {LOG_DIR}")

# Check if config directory exists
config_dir = os.path.dirname(CONFIG_PATH)
if not os.path.exists(config_dir):
    print(f"[WARNING] Config directory does not exist: {config_dir}")
    os.makedirs(config_dir, exist_ok=True)
    print(f"[INFO] Created config directory: {config_dir}")

# Load and configure logging
config_loaded = False
try:
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config file not found at: {CONFIG_PATH}")

    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

        # Inject the absolute log file path
        log_file_path = os.path.join(LOG_DIR, "app.log")
        config["handlers"]["file"]["filename"] = log_file_path

        print(f"[DEBUG] Log file will be created at: {log_file_path}")

        logging.config.dictConfig(config)
        config_loaded = True
        print("[DEBUG] ✓ Logging config loaded successfully from YAML")

except FileNotFoundError:
    print(f"[ERROR] Config file not found: {CONFIG_PATH}")
    print("[INFO] Using fallback logging configuration with file handler")

    # Fallback configuration with BOTH console and file handlers
    log_file_path = os.path.join(LOG_DIR, "app.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s",
        handlers=[
            logging.StreamHandler(),  # Console
            logging.FileHandler(log_file_path, encoding="utf8"),  # File
        ],
    )
    print(f"[INFO] Fallback logging configured with file: {log_file_path}")

except Exception as e:
    print(f"[ERROR] Failed to load logging config: {e}")
    import traceback

    traceback.print_exc()

    # Fallback with file handler
    log_file_path = os.path.join(LOG_DIR, "app.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file_path, encoding="utf8"),
        ],
    )

# Get logger AFTER config is loaded
logger = logging.getLogger("app_logger")

# Test that logging works
logger.info("=" * 50)
logger.info("Logging system initialized successfully")
logger.info(f"Log file location: {os.path.join(LOG_DIR, 'app.log')}")
logger.info(f"Config loaded from YAML: {config_loaded}")

# Test file logging explicitly
test_log_path = os.path.join(LOG_DIR, "app.log")
if os.path.exists(test_log_path):
    file_size = os.path.getsize(test_log_path)
    logger.info(f"✓ Log file exists! Size: {file_size} bytes")
    print(f"[DEBUG] ✓ Log file exists at {test_log_path} ({file_size} bytes)")
else:
    logger.warning(f"✗ Log file NOT found at {test_log_path}")
    print(f"[WARNING] ✗ Log file NOT found at {test_log_path}")

logger.info("=" * 50)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        url = str(request.url)

        logger.info(f"Incoming: {method} {url} from {client_ip}")

        status_code = 500
        response = None

        try:
            response = await call_next(request)
            status_code = response.status_code

            process_time = time.time() - start_time
            logger.info(
                f"Completed: {method} {url} | Status: {status_code} | Time: {process_time:.3f}s"
            )

            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Failed: {method} {url} | Error: {str(e)} | Time: {process_time:.3f}s",
                exc_info=True,
            )
            raise
