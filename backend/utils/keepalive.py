import requests
import time
from threading import Thread
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KeepAliveSystem:
    def __init__(self, url: str, interval: int = 840):  # 14 minutes
        self.url = url
        self.interval = interval
        self.thread = None
        self.running = False

    def _ping(self):
        try:
            response = requests.get(f"{self.url}/api/health")
            if response.status_code == 200:
                logger.info("Keepalive ping successful")
            else:
                logger.warning(f"Keepalive ping failed with status {response.status_code}")
        except Exception as e:
            logger.error(f"Keepalive ping error: {str(e)}")

    def _run(self):
        while self.running:
            self._ping()
            time.sleep(self.interval)

    def start(self):
        self.running = True
        self.thread = Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("Keepalive system started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            logger.info("Keepalive system stopped")
