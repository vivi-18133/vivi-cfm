import os
import logging
import shutil
from pathlib import Path
from vivicfm.AviMetaEdit import AviMetaEdit
from vivicfm.CFMFileRW import CFMFileRW
from vivicfm.CFMOutputDirectory import CFMOutputDirectory
from vivicfm.ConsoleProgressBar import ConsoleProgressBar
from vivicfm.ExifTool import ExifTool

LOGGER = logging.getLogger('cfm')


class MetadataManager:
    IMAGES_UPDATABLE_BY_EXIF_TOOL = [".jpg", ".jpeg"]
    VIDEOS_UPDATABLE_BY_EXIF_TOOL = [".mp4", ".mov"]
    VIDEOS_UPDATABLE_BY_AVI_META_EDIT = [".avi"]
    EXIF_TOOL_CACHE = "cache-exif-tool.json"

    def __init__(self, use_cache=True):
        self.exif_tool = None
        self.exif_tool_is_started = False
        self.avi_meta_edit = AviMetaEdit()
        self.data_read_by_exif_tool = {}
        self.cached_data_read_by_exif_tool = {}
        self.use_cache = use_cache
        if self.use_cache:
            self.load_cache()

    def __enter__(self):
        self.start_exif_tool()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_exif_tool()

    def create_exif_tool(self):
        self.exif_tool = ExifTool(stdout_file_path=CFMOutputDirectory.path / "exif-stdout.txt",
                                  stderr_file_path=CFMOutputDirectory.path / "exif-stderr.txt")

    def start_exif_tool(self):
        if self.exif_tool is None:
            self.create_exif_tool()
        if not self.exif_tool_is_started:
            self.exif_tool.start()
            self.exif_tool_is_started = True

    def stop_exif_tool(self):
        if self.exif_tool_is_started:
            if self.use_cache:
                self.save_cache()
            self.exif_tool.stop()
            self.exif_tool_is_started = False

    def batch_get_cm(self, file_list, title, force_reload=False):
        result = {}
        progress = ConsoleProgressBar(len(file_list), title)
        try:
            for file in file_list:
                result[file] = self.get_model_or_source(file, force_reload)
                progress.increment()
        finally:
            progress.stop()
            self.stop_exif_tool()
        return result

    def get_model_or_source(self, file_path, force_reload=False):
        if file_path not in self.data_read_by_exif_tool or force_reload:
            self.start_exif_tool()
            self.data_read_by_exif_tool[file_path] = self.exif_tool.get_model_or_source(file_path)
        return self.data_read_by_exif_tool[file_path]

    def batch_update_cm(self, file_list, title):
        progress = ConsoleProgressBar(len(file_list), title)
        try:
            for file, model in file_list.items():
                error = self.update_model_or_source(file, model)
                progress.increment(error)
        finally:
            progress.stop()
            self.stop_exif_tool()

    def update_model_or_source(self, file_path, new_model):
        self.save_original(file_path)
        filename = Path(file_path).name
        ext = os.path.splitext(filename)[1].lower()

        if ext in MetadataManager.IMAGES_UPDATABLE_BY_EXIF_TOOL:
            self.start_exif_tool()
            error = self.exif_tool.update_model(file_path, new_model)

        elif ext in MetadataManager.VIDEOS_UPDATABLE_BY_EXIF_TOOL:
            self.start_exif_tool()
            error = self.exif_tool.update_source(file_path, new_model)

        elif ext in MetadataManager.VIDEOS_UPDATABLE_BY_AVI_META_EDIT:
            error = self.avi_meta_edit.update_source(file_path, new_model)
        else:
            error = "Metadata of this file can't be updated with this version of the tool: %s" % filename
        return error

    def batch_revert(self, file_list):
        reverted_files = []
        progress = ConsoleProgressBar(len(file_list), "Revert all files previously saved")
        try:
            for file_path in file_list:
                reverted = self.restore_original(file_path)
                if reverted:
                    reverted_files.append(file_path)
                progress.increment()
        finally:
            progress.stop()
        return reverted_files

    def load_cache(self):
        self.load_data_read_by_exif_tool()

    def save_cache(self):
        self.save_data_read_by_exif_tool()

    def save_data_read_by_exif_tool(self):
        if self.data_read_by_exif_tool != self.cached_data_read_by_exif_tool:
            self.cached_data_read_by_exif_tool = self.data_read_by_exif_tool.copy()
            CFMFileRW.save_dict(self.cached_data_read_by_exif_tool, MetadataManager.EXIF_TOOL_CACHE)

    def load_data_read_by_exif_tool(self):
        self.cached_data_read_by_exif_tool = CFMFileRW.load_dict(MetadataManager.EXIF_TOOL_CACHE)
        if self.cached_data_read_by_exif_tool is not None:
            self.data_read_by_exif_tool = self.cached_data_read_by_exif_tool.copy()

    @staticmethod
    def save_original(file_path):
        original_renamed = file_path + ".original"
        if not os.path.exists(original_renamed):
            os.rename(file_path, original_renamed)
            shutil.copy2(original_renamed, file_path)

    @staticmethod
    def restore_original(file_path):
        original_file = file_path + ".original"
        if os.path.exists(original_file):
            os.remove(file_path)
            os.rename(original_file, file_path)
            return True
        return False
