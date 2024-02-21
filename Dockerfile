FROM python:3.11

WORKDIR /app
COPY . /app/

RUN apt-get update && apt-get install -y curl && apt-get clean
RUN pip install -r req/prod.txt

CMD python manage.py migrate \
    && python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'broteamracing@yandex.ru', 'qwertycvbn')" \
    && python manage.py collectstatic --no-input \
    && gunicorn -b 0.0.0.0:8000 btr.wsgi:application