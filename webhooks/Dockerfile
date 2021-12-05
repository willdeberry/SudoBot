FROM alpine:latest

LABEL maintainer="Will DeBerry <willdeberry@gmail.com>"

EXPOSE 8080

RUN apk add --no-cache uwsgi-python3 python3 py3-pip gcc python3-dev libc-dev libffi-dev make

COPY requirements.txt /tmp/webhooks_requirements.txt
RUN pip install --no-cache-dir -r /tmp/webhooks_requirements.txt

CMD [ "uwsgi", "--ini", "/var/www/sudobot/uwsgi.ini", "--uid", "uwsgi" ]
