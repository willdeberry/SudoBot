FROM alpine:latest

LABEL maintainer="Will DeBerry <willdeberry@gmail.com>"

RUN apk add --no-cache python3 py3-pip gcc python3-dev libc-dev libffi-dev make tzdata

COPY requirements.txt /tmp/service_requirements.txt
RUN pip install --no-cache-dir -r /tmp/service_requirements.txt
RUN pip list

ENV TZ=America/New_York

CMD [ "python3", "/usr/bin/sudobot/sudobot.py" ]
