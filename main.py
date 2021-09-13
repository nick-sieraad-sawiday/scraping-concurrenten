import logging
from time import sleep

from src.omnia import main as run_omnia
from src.maxaro import main as run_maxaro
from src.sanitairkamer import main as run_sanitairkamer
from src.tegeldepot import main as run_tegeldepot
from src.x2o import main as run_x2o
from src.combine import main as run_combine


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

    logger.info('omnia')
    omnia = run_omnia()
    sleep(3)
    logger.info('maxaro')
    run_maxaro(omnia)
    sleep(3)
    logger.info('sanitairkamer')
    run_sanitairkamer(omnia)
    sleep(3)
    logger.info('tegeldepot')
    run_tegeldepot(omnia)
    sleep(3)
    logger.info('x2o')
    run_x2o(omnia)
    logger.info('combine')
    run_combine()


if __name__ == '__main__':
    main()
