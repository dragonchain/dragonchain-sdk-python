FROM python:3.8

WORKDIR /usr/src/sdk
COPY requirements.txt /
COPY dev_requirements.txt /
RUN python3 -m pip install -r /requirements.txt && \
    python3 -m pip install -r /dev_requirements.txt

CMD [ "sh", "run.sh", "full-build" ]
