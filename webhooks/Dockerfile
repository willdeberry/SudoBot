FROM alpine:latest

LABEL maintainer="Will DeBerry <willdeberry@gmail.com>"

EXPOSE 8080

RUN apk add --no-cache uwsgi-python3 python3 py3-pip gcc python3-dev libc-dev libffi-dev make tzdata

COPY requirements.txt /tmp/webhooks_requirements.txt
RUN pip install --break-system-packages --no-cache-dir -r /tmp/webhooks_requirements.txt

ENV TZ=America/New_York
CMD [ "uwsgi", "--ini", "/var/www/sudobot/uwsgi.ini", "--uid", "uwsgi" ]
