dev:
	python3 manage.py runserver

collectstatic:
	python3 manage.py collectstatic --clear --ignore 'admin'

migrate:
	python3 manage.py makemigrations
	python3 manage.py migrate

celery-run:
	celery -A btr worker -l info