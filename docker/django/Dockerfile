FROM python:3.11.7-bullseye

# Copy scripts
COPY ./docker/django/scripts /django_scripts
## Add execution permissions
RUN find /django_scripts -type f -name "*.sh" -exec chmod +x {} \;

# Copy initial data
COPY ./docker/django/initial_data /initial_data

# Copy extra binaries
COPY ./docker/django/extras /tmp/extras

# Install dockerize to avoid startup problems (waiting for DB to start)
RUN tar xvzf /tmp/extras/dockerize/dockerize-linux-amd64-v0.7.0.tar.gz -C /usr/local/bin/

WORKDIR /currency_exchange_platform

COPY ./src/requirements.txt /currency_exchange_platform/
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /currency_exchange_platform/

# Use this command to run django
#CMD ["/django_scripts/run_django.sh"]
