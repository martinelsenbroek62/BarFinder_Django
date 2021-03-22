from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel
from ckeditor.fields import RichTextField


class Page(TimeStampedModel):
    TYPE = Choices(
        ('terms', 'terms'),
        ('policy', 'policy'),
        ('faq', 'faq')
    )

    title = models.CharField(max_length=100)
    slug = models.CharField(unique=True, choices=TYPE, max_length=6)
    short_description = models.CharField(max_length=255, blank=True, null=True)
    text = RichTextField()
    is_published = models.BooleanField(default=False)

    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta(object):
        ordering = ['order']

    def __str__(self):
        return self.title
