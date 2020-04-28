import locale
import subprocess
import logging
from pathlib import Path

LOGGER = logging.getLogger('cfm')
THIS_FILE_PATH = Path(__file__).parent
BIN_PATH = THIS_FILE_PATH / "bin"
AVI_META_EDIT_EXE = (BIN_PATH / "avimetaedit-1.0.2.exe").resolve()


class AviMetaEdit(object):
    NOTHING_TO_DO = "Nothing to do"
    IS_MODIFIED = "Is modified"

    def __init__(self, executable=AVI_META_EDIT_EXE):
        self.executable = executable

    def execute(self, *args):
        result = subprocess.run([self.executable] + list(args), stdout=subprocess.PIPE)
        return result.stdout.decode(locale.getpreferredencoding())

    def update_source(self, filename, new_model):
        result = self.execute("-v", "--ISRC=%s" % new_model, filename)
        if AviMetaEdit.IS_MODIFIED not in result and AviMetaEdit.NOTHING_TO_DO not in result:
            return "Error when trying to update %s" % filename
            # LOGGER.error("avimetaedit.exe output: %s" % result)
        return ""
