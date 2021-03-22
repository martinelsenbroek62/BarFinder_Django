import requests
import datetime
from constance import config
from django.conf import settings
from django.db import models
from django.db.models import F
from django.utils import timezone
from django.utils.translation import ugettext as _
from model_utils.models import TimeStampedModel

from structlog import get_logger

from good_spot.proxy.exceptions import IPOverUsageException, IPOverTimeException

log = get_logger()


class Proxy(TimeStampedModel):
    api_url = "http://seo-proxies.com/api.php"

    external_ip = models.CharField(max_length=30, unique=True)
    count = models.PositiveSmallIntegerField(default=0)
    last_usage = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = _("Proxies")

    @classmethod
    def max_count(cls):
        params = {
            "api": 1,
            "uid": settings.SEOPROXY_APIUSERID,
            "pwd": settings.SEOPROXY_APIKEY,
            "cmd": "hello"
        }
        hello_response = requests.get(
            url=cls.api_url,
            params=params
        ).content.decode("utf-8")
        hello_response = hello_response.split(":")

        assert len(hello_response) == 3
        assert hello_response[0] == "HELLO"

        ips_count = int(hello_response[2])
        return ips_count

    @classmethod
    def rotate(cls):
        params = {
            "api": 1,
            "uid": settings.SEOPROXY_APIUSERID,
            "pwd": settings.SEOPROXY_APIKEY,
            "cmd": "rotate"
        }

        rotate_response = requests.get(
            url=cls.api_url,
            params=params
        ).content.decode("utf-8")

        rotate_response = rotate_response.split(":")

        assert len(rotate_response) == 4
        assert rotate_response[0] == "ROTATE"

        if not cls.objects.filter(external_ip=rotate_response[3]).exists():
            obj = cls.objects.create(
                external_ip=rotate_response[3],
                count=0
            )
        else:
            obj = cls.objects.get(external_ip=rotate_response[3])
            if obj.count >= config.MAX_REQUESTS_PER_HOUR:
                raise IPOverUsageException
            if (timezone.now() - obj.last_usage) < datetime.timedelta(
                    minutes=config.DELAY_BETWEEN_PROXY_REQUESTS_IN_MINUTES
            ):
                raise IPOverTimeException

        rotate_response_dict = {
            "proxy_url": "{}:{}".format(rotate_response[1], rotate_response[2]),
            "proxy_external_ip": rotate_response[3]
        }

        return rotate_response_dict

    @classmethod
    def count_ip(cls, ip):
        updated = cls.objects.filter(
            external_ip=ip
        ).update(
            count=F('count') + 1,
            last_usage=timezone.now()
        )
        if not updated:
            cls.objects.create(
                external_ip=ip,
                count=1
            )
