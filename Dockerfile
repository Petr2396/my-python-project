FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# collect static в контейнере при сборке можно, но для production лучше в CI
CMD ["gunicorn", "shop.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "90"]
