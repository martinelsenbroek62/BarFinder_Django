import boto3
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
from structlog import get_logger

from good_spot.images.models import PlaceImage

log = get_logger()


@receiver(post_delete, sender=PlaceImage)
def remove_item_from_s3(instance, **kwargs):
    try:
        client_kwargs = {}
        if not settings.AWS_S3_USE_ROLES:
            client_kwargs['aws_access_key_id'] = settings.AWS_ACCESS_KEY_ID
            client_kwargs['aws_secret_access_key'] = settings.AWS_SECRET_ACCESS_KEY
        client = boto3.client('s3', **client_kwargs)

        client.delete_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=str(instance.image)
        )

        if instance.thumbnail:
            client.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=str(instance.thumbnail)
            )
    except Exception as e:
        print(e)
        log.error("Something went wrong when tries remove PlaceImage ID={} from S3".format(instance.id))
