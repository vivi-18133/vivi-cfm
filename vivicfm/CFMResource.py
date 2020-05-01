import json
import sys
import os
from pathlib import Path


class CFMResource:

    logging_configuration = None
    cfm_configuration = None

    @staticmethod
    def init():
        try:
            wd = sys._MEIPASS
        except AttributeError:
            wd = os.getcwd()
        logging_configuration_file = Path(wd) / "conf" / "logging.json"
        cfm_configuration_file = Path(wd) / "conf" / "cfm.json"
        for filename in os.listdir(Path(wd)):
            print(filename)
        for filename in os.listdir(Path(wd) / "bin"):
            print(filename)
        with open(logging_configuration_file, 'r') as f:
            CFMResource.logging_configuration = json.load(f)
        with open(cfm_configuration_file, 'r') as f:
            CFMResource.cfm_configuration = json.load(f)

