#! /bin/bash

sudo docker-compose build
# sudo docker-compose up

sudo docker-compose run --rm gesfipe_app /bin/bash -c "./manage.py makemigrations"
sudo docker-compose run --rm gesfipe_app /bin/bash -c "./manage.py migrate"
sudo docker-compose run --rm gesfipe_app /bin/bash -c "./manage.py collectstatic"
sudo docker-compose run --rm gesfipe_app /bin/bash -c "./manage.py createsuperuser"

sudo docker-compose up

# sudo docker-compose run --rm djangoapp /bin/bash -c "cd hello; ./manage.py migrate"
# sudo docker-compose run djangoapp hello/manage.py collectstatic --no-input
# sudo docker-compose run djangoapp hello/manage.py createsuperuser
