import logging
import logging.config
import os
import time
from threading import Thread

import requests
import yaml
from keys.telegram import TELEGRAM_CHAT_ID, TELEGRAM_TOKEN
from keys.nym import NYM_HOST, NYM_DESC_PORT

logging_yaml_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "resources", "logging_config.yaml")
)


def setup_logging():
    with open(logging_yaml_path, "r") as f:
        config = yaml.safe_load(f.read())
        config["handlers"]["telegram"]["token"] = TELEGRAM_TOKEN
        config["handlers"]["telegram"]["chat_id"] = TELEGRAM_CHAT_ID
        logging.config.dictConfig(config)


def checkState(host, port):
    desc_url = "http://{}:{}/description".format(host, port)
    logger.debug("Check URL: {}".format(desc_url))
    try:
        desc_request = requests.get(desc_url)
        if desc_request.status_code != 200:
            logger.error("NYM node {}:{} seems to be offline".format(host, port))
        else:
            logger.debug("NYM node online!")
    except Exception as err:
        logger.error("NYM node {}:{} seems to be offline".format(host, port))


def worker(host, sleep_time):
    while True:
        checkState(host)
        time.sleep(sleep_time)


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Monitoring NYM node at {} now!".format(NYM_HOST))
    t = Thread(target=worker, args=(NYM_HOST, NYM_DESC_PORT, 60, ))
    t.start()
