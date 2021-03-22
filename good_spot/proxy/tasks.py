from structlog import get_logger

from good_spot.proxy.models import Proxy
from good_spot.taskapp.celery import app

log = get_logger()


@app.task
def run_periodic_reset_counter():
    log.info('Ran reset counter of IP usage.')
    Proxy.objects.update(count=0)
