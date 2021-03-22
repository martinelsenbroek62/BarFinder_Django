from django.db import models
from model_utils.models import TimeStampedModel


class Report(TimeStampedModel):
    email = models.EmailField()
    message = models.TextField()
    app_version = models.CharField(max_length=20)

    def __str__(self):
        return "{} {}".format(self.app_version, self.email)
