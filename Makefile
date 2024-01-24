install:
	poetry install

dev:
	python3 manage.py runserver

collectstatic:
	python3 manage.py collectstatic --clear --ignore 'admin'

migrate:
	poetry run python3 manage.py makemigrations
	poetry run python3 manage.py migrate

celery-run:
	celery -A btr worker -l info

celery-beat:
	celery -A btr beat -l info

redis-run:
	docker run -d -p 6379:6379 redis

bot:
	python3 manage.py run_bot

shell:
	python3 manage.py shell

messages:
	python3 manage.py makemessages --ignore="static" -l ru

compile:
	python3 manage.py compilemessages

lint:
	poetry run flake8 --exclude=static,*migrations,settings.py

test:
	docker-compose -f docker-compose.test.yml up -d && poetry run python3 manage.py test && docker-compose -f docker-compose.test.yml down

test-coverage:
	docker-compose -f docker-compose.test.yml up -d && poetry run coverage run manage.py test && poetry run coverage report -m --include=btr/* --omit=btr/settings.py && poetry run coverage xml --include=btr/* --omit=btr/settings.py && docker-compose -f docker-compose.test.yml down