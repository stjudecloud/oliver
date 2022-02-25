FROM python:3.10.2-bullseye

RUN apt-get update \
    && apt-get install -y --no-install-recommends jq \
    && rm -rf /var/lib/apt/lists/*

ENV OLIVER_HOME=/opt/oliver
ENV PYTHONWARNINGS="ignore"
WORKDIR $OLIVER_HOME

RUN pip install --disable-pip-version-check \
    --no-cache-dir \
    setuptools poetry httpie
COPY poetry.lock pyproject.toml ${OLIVER_HOME}/
COPY README.md ${OLIVER_HOME}/README.md
COPY oliver/ ${OLIVER_HOME}/oliver/
COPY tests/ ${OLIVER_HOME}/tests/

RUN poetry config --local virtualenvs.create false
RUN poetry install
ENTRYPOINT ["oliver"]