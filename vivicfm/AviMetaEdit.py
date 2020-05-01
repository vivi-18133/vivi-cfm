import locale
import subprocess
import logging

from vivicfm.CFMResource import CFMResource

LOGGER = logging.getLogger('cfm')


class AviMetaEdit(object):
    NOTHING_TO_DO = "Nothing to do"
    IS_MODIFIED = "Is modified"

    def __init__(self, executable=None):
        self.executable = executable
        if self.executable is None:
            self.executable = CFMResource.avimetaedit_executable

    def execute(self, *args):
        result = subprocess.run([self.executable] + list(args), stdout=subprocess.PIPE)
        return result.stdout.decode(locale.getpreferredencoding())

    def update_source(self, filename, new_model):
        result = self.execute("-v", "--ISRC=%s" % new_model, filename)
        if AviMetaEdit.IS_MODIFIED not in result and AviMetaEdit.NOTHING_TO_DO not in result:
            return "Error when trying to update %s" % filename
            # LOGGER.error("avimetaedit.exe output: %s" % result)
        return ""
