import jwt
import os
import requests

notifier_url = os.environ.get('NOTIFIER_URL')
secret = os.environ.get('NOTIFIER_SECRET')


def handler(event, context):
    for record in event['Records']:
        key = record['s3']['object']['key']
        filename = key.replace('resized-images/', '')
        payload = {
            'filename': filename
        }

        encoded = jwt.encode(payload, secret, algorithm='HS256')

        resp = requests.post(notifier_url, data={'payload': encoded.decode('ascii')})
        if resp.status_code != 200:
            print(resp.content)
            print('Notified finished with {} status code'.format(resp.status_code))
        else:
            print('Successfully notified with {} status code'.format(resp.status_code))
