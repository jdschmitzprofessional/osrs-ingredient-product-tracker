FROM python:3.12


COPY --chmod=777 src /opt/src

RUN pip install -r /opt/src/requirements.txt

WORKDIR /opt/src

ENTRYPOINT python /opt/src/main.py