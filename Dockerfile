FROM python:3.8.1

ENV OLIVER_HOME=/opt/oliver
WORKDIR $OLIVER_HOME

COPY README.md ${OLIVER_HOME}/README.md
COPY setup.py ${OLIVER_HOME}/setup.py
COPY requirements.txt ${OLIVER_HOME}/requirements.txt
COPY oliver/ ${OLIVER_HOME}/oliver/
COPY scripts/ ${OLIVER_HOME}/scripts/
COPY tests/ ${OLIVER_HOME}/tests/

RUN python3 setup.py install