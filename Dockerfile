FROM python:3.8.1

RUN apt-get update \
    && apt-get install -y --no-install-recommends httpie jq \
    && rm -rf /var/lib/apt/lists/*

ENV OLIVER_HOME=/opt/oliver
ENV PYTHONWARNINGS="ignore"
WORKDIR $OLIVER_HOME

COPY requirements.txt ${OLIVER_HOME}/requirements.txt
RUN pip install -r requirements.txt

COPY README.md ${OLIVER_HOME}/README.md
COPY setup.py ${OLIVER_HOME}/setup.py
COPY oliver/ ${OLIVER_HOME}/oliver/
COPY bin/ ${OLIVER_HOME}/bin/
COPY tests/ ${OLIVER_HOME}/tests/

RUN python3 setup.py develop
ENTRYPOINT ["oliver"]