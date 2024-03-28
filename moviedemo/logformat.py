##
##

import logging
import moviedemo.constants as C


class CustomDisplayFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: f"[{C.GREY_COLOR}{C.FORMAT_LEVEL}{C.SCREEN_RESET}] {C.FORMAT_MESSAGE}",
        logging.INFO: f"[{C.GREEN_COLOR}{C.FORMAT_LEVEL}{C.SCREEN_RESET}] {C.FORMAT_MESSAGE}",
        logging.WARNING: f"[{C.YELLOW_COLOR}{C.FORMAT_LEVEL}{C.SCREEN_RESET}] {C.FORMAT_MESSAGE}",
        logging.ERROR: f"[{C.RED_COLOR}{C.FORMAT_LEVEL}{C.SCREEN_RESET}] {C.FORMAT_MESSAGE}",
        logging.CRITICAL: f"[{C.BOLD_RED_COLOR}{C.FORMAT_LEVEL}{C.SCREEN_RESET}] {C.FORMAT_MESSAGE}"
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        if logging.DEBUG >= logging.root.level:
            log_fmt += C.FORMAT_EXTRA
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class CustomLogFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: f"{C.FORMAT_TIMESTAMP} [{C.FORMAT_LEVEL}] {C.FORMAT_MESSAGE}",
        logging.INFO: f"{C.FORMAT_TIMESTAMP} [{C.FORMAT_LEVEL}] {C.FORMAT_MESSAGE}",
        logging.WARNING: f"{C.FORMAT_TIMESTAMP} [{C.FORMAT_LEVEL}] {C.FORMAT_MESSAGE}",
        logging.ERROR: f"{C.FORMAT_TIMESTAMP} [{C.FORMAT_LEVEL}] {C.FORMAT_MESSAGE}",
        logging.CRITICAL: f"{C.FORMAT_TIMESTAMP} [{C.FORMAT_LEVEL}] {C.FORMAT_MESSAGE}"
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        if logging.DEBUG >= logging.root.level:
            log_fmt += C.FORMAT_EXTRA
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
