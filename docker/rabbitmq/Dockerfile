FROM rabbitmq:3.12.12-management

RUN rabbitmq-plugins enable --offline rabbitmq_top

# https://www.rabbitmq.com/configure.html#configuration-file
COPY ./docker/rabbitmq/rabbitmq.conf /etc/rabbitmq/rabbitmq_custom.conf
ENV RABBITMQ_CONFIG_FILE=/etc/rabbitmq/rabbitmq_custom
