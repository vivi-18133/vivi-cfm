#!/bin/env python

import threading
import time
import sys
from datetime import datetime

PROGRESS_BAR_SIZE = 40
WINDOW_WIDTH = 150  # TODO
REFRESH_DELAY = 0.05

REMAINING_TIME_STR_MAX_SIZE = 12

SPACE = " "
BAR_CHAR = "#"
DEFIL_CHARACTERS = ["/", "-", "\\", "|"]


class ConsoleProgressBar:

    # --------------------------------------------------------
    def __init__(self, max, title="", clear_screen=False):

        self.title = title
        if self.title != "":
            self.title = "[%s] %s" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3], self.title)

        self.defil_position = 0
        self.position = 0
        self.max = max
        self.text = []
        self.run = True
        self.start_time = time.time()
        self.remaining_time_str = ""
        self.clear_screen = clear_screen
        self.lock_increment = threading.Lock()

        thread = threading.Thread(None, self.auto_refresh, None, [], {})
        thread.start()

    # --------------------------------------------------------
    def compute_remaining_time(self):

        if self.position > 0:
            current_time = time.time()
            rem_time = ((current_time - self.start_time) / self.position) * (self.max - self.position)

            hour = int(rem_time / 3600)
            min = str(int((rem_time - hour * 3600) / 60)).zfill(2)
            sec = str(int((rem_time - hour * 3600) % 60)).zfill(2)

            self.remaining_time_str = ""
            if hour != 0:
                self.remaining_time_str += "%sh" % (hour)
            if min != "00":
                self.remaining_time_str += " %sm" % (min)

            self.remaining_time_str += " %ss" % (sec)
            for i in range(REMAINING_TIME_STR_MAX_SIZE - len(self.remaining_time_str)):
                self.remaining_time_str += SPACE

    # --------------------------------------------------------
    def multi_increment(self, n, text=""):
        with self.lock_increment:
            self.position += n
            self.text.append(text)
            self.compute_remaining_time()

            if self.position >= self.max:
                self.run = False
                time.sleep(2 * REFRESH_DELAY)


    # --------------------------------------------------------
    def increment(self, text=""):
        with self.lock_increment:
            self.position += 1
            self.text.append(text)
            self.compute_remaining_time()

            if self.position >= self.max:
                self.run = False
                time.sleep(2 * REFRESH_DELAY)

    # --------------------------------------------------------
    def auto_refresh(self):

        while self.run:
            time.sleep(REFRESH_DELAY)
            self.refresh()
        self.refresh()

        if self.clear_screen:
            sys.stdout.write("\r")
            for i in range(WINDOW_WIDTH):
                sys.stdout.write(" ")
            sys.stdout.write("\r")
        else:
            print("")

    # --------------------------------------------------------
    def stop(self):
        self.run = False
        time.sleep(2 * REFRESH_DELAY)

    # --------------------------------------------------------
    def refresh(self):

        sys.stdout.write("\r")

        if self.max == 0:
            return

        self.defil_position += 1
        position_100 = self.position * 100 / self.max
        position_progress_bar = position_100 * PROGRESS_BAR_SIZE / 100

        bar = ""
        for i in range(PROGRESS_BAR_SIZE):
            if i < position_progress_bar:
                bar += BAR_CHAR
            elif i == position_progress_bar:
                bar += DEFIL_CHARACTERS[self.defil_position % len(DEFIL_CHARACTERS)]
            else:
                bar += SPACE

        for text in self.text:
            if text != "":
                for i in range(WINDOW_WIDTH - len(text)):
                    text += SPACE

                sys.stdout.write(text[:-1] + "\n")

        self.text = []

        sys.stdout.write("%s [%s] %s/%s (%d%s) %s" % (
            self.title, bar, self.position, self.max, position_100, "%", self.remaining_time_str))


# ---------------------------------------------------------------------------------------
if __name__ == "__main__":

    progress_bar = ConsoleProgressBar(10)

    for i in range(1, 11):
        time.sleep(1)
        progress_bar.increment("etape : %i" % i)
