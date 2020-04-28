import sys
import json
import logging
import logging.config
from pathlib import Path

from vivicfm.CFMOutputDirectory import CFMOutputDirectory
from vivicfm.CameraModelProcessor import CameraModelProcessor

THIS_FILE_PATH = Path(__file__).parent
BASE_OUTPUT_PATH = Path("output")
LOGGING_CONF_FILE = THIS_FILE_PATH / "conf" / "logging.json"
LOGGER = logging.getLogger('cfm')


def configure_logging():
    with open(LOGGING_CONF_FILE, 'r') as f:
        log_cfg = json.load(f)
        logging.config.dictConfig(log_cfg)


def execute_program(options):
    input_dir_path = Path(options[1])

    action = "camera-model-check"
    if len(options) > 2:
        action = options[2]

    CFMOutputDirectory.init(BASE_OUTPUT_PATH, input_dir_path)

    if action == "camera-model-check":
        with CameraModelProcessor(input_dir_path, try_load_cache=True) as cmp:
            cmp.analyze()
            cmp.apply()

    if action == "revert":
        with CameraModelProcessor(input_dir_path, try_load_cache=True) as cmp:
            cmp.revert()


    # duplicationAnalysis = DuplicationAnalysis(input_dir_path, output_dir_path)
    # duplicationAnalysis.computeDuplicated(print_stats=True, save_results=True)

def main():
    configure_logging()
    try:
        LOGGER.info("cfm started with options: %s" % " ".join(sys.argv))
        execute_program(sys.argv)
    finally:
        LOGGER.info("cfm ended")

if __name__ == '__main__':
    main()