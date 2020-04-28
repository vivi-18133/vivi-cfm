import os
import json
import locale
import logging
import subprocess
import time
from pathlib import Path

LOGGER = logging.getLogger('cfm')
THIS_FILE_PATH = Path(__file__).parent
BIN_PATH = THIS_FILE_PATH / "bin"
EXIF_TOOL_EXE = (BIN_PATH / "exiftool-11.94.exe").resolve()


class ExifTool(object):
    CHARSET_OPTION = ("-charset", "filename=" + locale.getpreferredencoding())
    IMAGE_UPDATE = "image files updated"
    SOURCE_METADATA = "Source"
    MODEL_METADATA = "Model"
    SENTINEL = "{ready}" + os.linesep

    def __init__(self, executable=EXIF_TOOL_EXE, stdout_file_path=None, stderr_file_path=None):
        self.executable = executable
        self.process = None
        self.stdout_file = None
        self.stderr_file = None
        if stdout_file_path is not None:
            self.stdout_file = open(stdout_file_path, "wb")
        if stderr_file_path is not None:
            self.stderr_file = open(stderr_file_path, "wb")

    def __del__(self):
        if self.stdout_file is not None:
            self.stdout_file.close()
        if self.stderr_file is not None:
            self.stderr_file.close()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        LOGGER.info("Starting %s", self.executable)
        self.process = subprocess.Popen(
            [self.executable, "-stay_open", "True", "-@", "-"],
            universal_newlines=True,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if self.stdout_file is not None:
            self.stdout_file.write("--\nExifTool started\n--\n".encode('utf-8'))
            self.stdout_file.flush()
        if self.stderr_file is not None:
            self.stderr_file.flush()

    def stop(self):
        LOGGER.info("Stopping %s", self.executable)
        self.process.stdin.write("-stay_open\nFalse\n")
        self.process.stdin.flush()
        if self.stdout_file is not None:
            self.stdout_file.write("--\nExifTool stopped\n--\n".encode('utf-8'))
            self.stdout_file.flush()
        if self.stderr_file is not None:
            self.stderr_file.write(self.process.stderr.read().encode('utf-8'))
            self.stderr_file.flush()

    def execute(self, *args):
        args = ExifTool.CHARSET_OPTION + args + ("-execute\n",)
        self.process.stdin.write(str.join("\n", args))
        self.process.stdin.flush()
        output = ""
        fd = self.process.stdout.fileno()
        while not output.endswith(self.SENTINEL):
            output += os.read(fd, 4096).decode('utf-8')
        return output[:-len(self.SENTINEL)]

    def write_stdout(self, stdout):
        if self.stdout_file is not None:
            self.stdout_file.write(stdout.encode('utf-8'))

    def get_model_or_source(self, filename):
        stdout = self.execute("-j", "-n", "-model", "-source", filename)
        self.write_stdout(stdout)
        result = json.loads(stdout)
        if len(result) == 0:
            return None
        if ExifTool.MODEL_METADATA in result[0]:
            return result[0][ExifTool.MODEL_METADATA]
        if ExifTool.SOURCE_METADATA in result[0]:
            return result[0][ExifTool.SOURCE_METADATA]
        return None

    def update_model(self, filename, new_model):
        stdout = self.execute("-overwrite_original", "-source=" + new_model, filename)
        self.write_stdout(stdout)
        if ExifTool.IMAGE_UPDATE not in stdout:
            return "Error when trying to update %s" % filename
        return ""

    def update_source(self, filename, new_model):
        stdout = self.execute("-overwrite_original", "-source=" + new_model, filename)
        self.write_stdout(stdout)
        if ExifTool.IMAGE_UPDATE not in stdout:
            return "Error when trying to update %s" % filename
        return ""