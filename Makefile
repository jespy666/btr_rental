dev:
	python3 manage.py runserver

collectstatic:
	python3 manage.py collectstatic --clear --ignore 'admin'