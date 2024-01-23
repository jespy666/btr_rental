dev:
	python3 manage.py runserver

collectstatic:
	python3 manage.py collectstatic --clear --ignore 'admin'

migrate:
	python3 manage.py makemigrations
	python3 manage.py migrate

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