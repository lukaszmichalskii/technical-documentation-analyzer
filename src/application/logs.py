import logging


def setup_logger(loggername='SKG', filename='execution.log') -> logging.Logger:
    logger = logging.Logger(loggername)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s:\t%(module)s@%(lineno)s:\t%(message)s')
    console_formatter = logging.Formatter('[%(levelname)s]\t\t%(message)s')
    full = logging.FileHandler(filename, mode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(console_formatter)
    full.setLevel(logging.DEBUG)
    full.setFormatter(formatter)
    logger.addHandler(console)
    logger.addHandler(full)
    return logger
