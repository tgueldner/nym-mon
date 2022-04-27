import logging
import logging.config
import os
import time
from threading import Thread

import requests
import yaml
from keys.telegram import TELEGRAM_CHAT_ID, TELEGRAM_TOKEN
from keys.nym import NYM_HOST, NYM_DESC_PORT, NYM_EXPLORER_API

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


def worker(sleep_time):
    while True:
        checkState(NYM_HOST, NYM_DESC_PORT)
        time.sleep(sleep_time)


def getIdentityKey(host, port):
    url = "http://{}:{}/verloc".format(host, port)
    try:
        request = requests.get(url)
        if request.status_code != 200:
            logger.error("NYM node {}:{} seems to be offline".format(host, port))
            return
        else:
            data = request.json()
            return data["results"][0]["identity"]
    except Exception as err:
        logger.error("NYM node {}:{} seems to be offline".format(host, port))


def checkDelegation(id):
    url = NYM_EXPLORER_API+"/mix-node/{}".format(id)
    try:
        request = requests.get(url)
        if request.status_code == 200:
            data = request.json()
            return round(int(data["total_delegation"]["amount"])/1000000)
    except Exception as err:
        logger.error("Explorer Api seems to be offline")


def checkDelegationWorker(sleep_time, id):
    stake = 0
    while True:
        newStake = checkDelegation(id)
        if newStake != stake:
            stake = newStake
            logger.info("new stake for mixnode {}: {}".format(id, stake))
        time.sleep(sleep_time)


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)

    id = getIdentityKey(NYM_HOST, NYM_DESC_PORT)

    logger.info("Monitoring NYM node at {}:{} ({})!".format(NYM_HOST, NYM_DESC_PORT, id))
    Thread(target=worker, args=(60, )).start()
    Thread(target=checkDelegationWorker, args=(60 * 60, id, )).start()
