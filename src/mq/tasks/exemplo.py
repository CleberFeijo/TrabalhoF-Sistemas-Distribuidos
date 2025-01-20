from time import sleep

from common.functions import time_to_seconds
from core.loggers import Loggers
from utils.celery import Task

from ..routes import CeleryTaskConf

__all__ = 'ExemploTask',


class ExemploTask(Task):
    name = CeleryTaskConf.EXEMPLO
    logger = Loggers('taskExemplo')
    soft_time_limit = time_to_seconds(minutes=2)

    def run(self):
        sleep(10)
        return 'OK'
