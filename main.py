from src.maxaro import main as run_maxaro
from src.tegeldepot import main as run_tegeldepot
from src.sanitairkamer import main as run_sanitairkamer
from src.x2o import main as run_x2o
import logging


def create_logger() -> logging.Logger:
    """
    Creates a logger to track the process

    :return: logger
    """

    logger = logging.getLogger("logging_tryout2")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


def main():

    logger = create_logger()

    logger.info('maxaro')
    run_maxaro()
    logger.info('tegeldepot')
    run_tegeldepot()
    logger.info('sanitairkamer')
    run_sanitairkamer()
    logger.info('x2o')
    run_x2o()


if __name__ == '__main__':
    main()
