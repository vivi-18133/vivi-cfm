import os
from pathlib import Path

videoExt = [".avi", ".mov", ".mp4"]
imageExt = [".jpg", ".jpeg", ".thm"]
audioExt = [".wav", ".mp3"]
mediaExt = videoExt + imageExt + audioExt


class CFMFileList:

    def __init__(self):
        self.files = {}
        self.ignored = {}
        self.total_number_of_files = 0
        self.all = []
        self.media = []

    def compute(self, input_dir_path):
        for (dir_path, folder_names, file_names) in os.walk(input_dir_path):
            for file_name in file_names:
                self.add(str(Path(dir_path) / file_name))

    def add(self, file):
        self.all.append(file)
        self.total_number_of_files += 1
        filename = Path(file).name
        ext = os.path.splitext(filename)[1].lower()
        if ext in mediaExt:
            self.media.append(file)
        if ext in self.files:
            self.files[ext] += 1
        else:
            self.files[ext] = 1

    def get_number_of(self, extList):
        result = 0
        for file_type in extList:
            if file_type in self.files:
                result += self.files[file_type]
        return result

    @staticmethod
    def print_ident(string):
        print("    " + string)

    def print(self):
        print("")
        print("-------------------------------------------------------------")
        print("")
        self.print_ident(".......................")
        self.print_ident("| Number of files: " + str(self.total_number_of_files))
        self.print_ident(".......................")
        self.print_ident("| Number of image files: " + str(self.get_number_of(imageExt)))
        self.print_ident("| Number of video files: " + str(self.get_number_of(videoExt)))
        self.print_ident("| Number of audio files: " + str(self.get_number_of(audioExt)))

        self.print_ident(".......................")
        self.print_ident("| Media files (" + str(self.get_number_of(mediaExt)) + " files)")
        for filetype in mediaExt:
            if filetype in self.files:
                self.print_ident("| " + filetype + ": " + str(self.files[filetype]))

        self.print_ident(".......................")
        self.print_ident("| Other files")
        for filetype, number in self.files.items():
            if filetype not in mediaExt:
                self.print_ident("| " + filetype + ": " + str(number))
        self.print_ident(".......................")
        print("")
