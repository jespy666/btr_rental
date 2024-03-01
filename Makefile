dev:
	python3 manage.py runserver --settings=config.settings

collectstatic:
	python3 manage.py collectstatic --ignore 'admin'

celery:
	celery -A btr worker -l info

celery-beat:
	celery -A btr beat -l info

redis:
	docker run -d -p 6379:6379 redis

bot:
	python3 manage.py run_bot

shell:
	python3 manage.py shell

messages:
	python3 manage.py makemessages --ignore="static,venv" -l ru

compile:
	python3 manage.py compilemessages

lint:
	flake8 --exclude=static,*migrations,venv,config

test:
	python3 manage.py test

test-coverage:
	coverage run manage.py test && coverage report -m --include=btr/* --omit=btr/config/settings.py && coverage xml --include=btr/* --omit=btr/config/settings.py
