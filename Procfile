web: gunicorn agendamento.wsgi --bind 0.0.0.0:$PORT
release: python manage.py migrate && python init_production.py