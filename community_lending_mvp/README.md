# Community Lending - Django Hackathon MVP

This is an MVP codebase for the Community Lending project (mobile-first micro-lending portal) built with Django.

Quick start:
1. python -m venv venv
2. source venv/bin/activate
3. pip install -r requirements.txt
4. python manage.py migrate
5. python manage.py createsuperuser
6. python manage.py runserver

Notes:
- Uses console email/SMS by default for fast development.
- Approve loans in Django admin to auto-generate installments (select loans and choose "Approve selected loans and generate installments").
- For reminders, run: `python manage.py send_reminders` (or use Celery beat in production).
