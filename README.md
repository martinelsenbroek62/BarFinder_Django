## Local deployment

* ``git clone``
* ``cd mygoodspot``
* ``vagrant up``
* ``vagrant ssh``
* ``cp env.example config/.env``

## Use ansible to update servers :

* ``cd ansible``
* ``ansible-playbook universal.yml --extra-vars="target=develop"``      (for develop)
* ``ansible-playbook universal.yml --extra-vars="target=staging"``      (for staging)
* ``ansible-playbook universal.yml --extra-vars="target=production"``   (for production)


* ``python manage.py update_translation_fields`` run this command every time new fiedls for translation added

## Run Celery worker

* ``celery -A good_spot.taskapp workers -l info``
* ``celery beat -A good_spot.taskapp -l info``

## Populate database with cities

* ``./manage.py cities_light``

## Proxy

We use http://proxies.com/
Please, add corresponding credentials into `.env`
* DJANGO_SEOPROXY_APIUSERID
* DJANGO_SEOPROXY_APIKEY
