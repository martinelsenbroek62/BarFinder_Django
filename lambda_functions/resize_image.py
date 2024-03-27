from __future__ import print_function

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import boto3
import uuid
import piexif

from PIL import Image

s3_client = boto3.client('s3')
file_sizes = [(480, 480, 3), ]


def prepare_resize_path(key, size=(200, 300)):
    path = key.split('.')
    first_part = '-'.join(path[:-1])
    second_part = path[-1]
    size_prefix = '_'.join(str(s) for s in size)

    return '{}_{}.{}'.format(first_part, size_prefix, second_part)


def resize_image(image_path, resized_path, size=(480, 480)):
    with Image.open(image_path) as image:
        exif_bytes = None
        if image._getexif():
            print(image._getexif().items())
            exif_dict = piexif.load(image.info["exif"])
            exif_bytes = piexif.dump(exif_dict)

        max_prev_size = max(image.size)
        min_prev_size = min(image.size)
        multiplier = max_prev_size / min_prev_size
        prev_width, prev_height = image.size  # Get dimensions
        print('prev params {} {}'.format(prev_width, prev_height))
        if prev_width > prev_height:
            new_size = (size[0] * multiplier, size[1])
        elif prev_height > prev_width:
            new_size = (size[0], size[1] * multiplier)
        else:
            new_size = size
        print('Thumb params {} {}'.format(*new_size))
        image.thumbnail(new_size, Image.ANTIALIAS)
        # save thumbnail with exif data

        width, height = image.size

        print('New params {} {}'.format(width, height))

        image = image.resize((width, height))
        if exif_bytes:
            image.save(resized_path, exif=exif_bytes)
        else:
            image.save(resized_path)


def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        filename = key.replace('images/', '')
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), filename)
        print('Key ' + key)
        print('FileName ' + filename)
        print('Path ' + download_path)

        for size in file_sizes:
            upload_path = '/tmp/{}{}'.format(uuid.uuid4(), filename)
            print('Upload path ' + download_path)
            s3_client.download_file(bucket, key, download_path)

            resize_image(download_path, upload_path, size=size)
            new_key = 'resized-images/{}'.format(filename)
            print('New Key ' + new_key)
            s3_client.upload_file(upload_path, bucket, new_key)
