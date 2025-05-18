LOCAL_WEB_CONTAINER_NAME=linkly
LOCAL_DB_CONTAINER_NAME=linkly.db
LOCAL_DOCKER_OPTIONS= -f docker-compose.yml


up:
	docker compose  $(LOCAL_DOCKER_OPTIONS) up -d

down:
	docker compose $(LOCAL_DOCKER_OPTIONS) down

stop:
	docker compose $(LOCAL_DOCKER_OPTIONS) stop

server:
	docker exec -it $(LOCAL_WEB_CONTAINER_NAME) python manage.py runserver 0:8000

collectstatic:
	docker exec -it $(LOCAL_WEB_CONTAINER_NAME) python manage.py collectstatic --noinput

build:
	docker compose $(LOCAL_DOCKER_OPTIONS) build

rebuild:
	docker-compose $(LOCAL_DOCKER_OPTIONS) build --force-recreate --no-deps

test:
	docker exec -it $(LOCAL_WEB_CONTAINER_NAME) pytest

ssh:
	docker exec -it $(LOCAL_WEB_CONTAINER_NAME) /bin/sh

superuser:
	docker exec -it $(LOCAL_WEB_CONTAINER_NAME) python manage.py createsuperuser

requirements:
	docker exec -it $(LOCAL_WEB_CONTAINER_NAME) pip install -r requirements.txt

migrations:
	docker exec -it $(LOCAL_WEB_CONTAINER_NAME) python manage.py makemigrations

migrate:
	docker exec -it $(LOCAL_WEB_CONTAINER_NAME) python manage.py migrate

db-shell:
	docker exec -it $(LOCAL_DB_CONTAINER_NAME) postgres
db-ssh:
	docker exec -it $(LOCAL_DB_CONTAINER_NAME) /bin/sh

flush:
	docker exec -it $(LOCAL_WEB_CONTAINER_NAME) python manage.py flush

apply-fixtures:
	docker exec -it $(LOCAL_WEB_CONTAINER_NAME) python manage.py loaddata fixtures/*.yaml
