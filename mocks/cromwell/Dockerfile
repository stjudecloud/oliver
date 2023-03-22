FROM broadinstitute/cromwell:86-b04d895
LABEL maintainer "St. Jude Cloud Team <support@stjude.cloud>"

ADD cromwell.conf /app/cromwell.conf
RUN apt-get update \
    && apt-get install -y --no-install-recommends wget git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/vishnubob/wait-for-it.git ${BIN_DIRECTORY}/wait-for-it/
ENV PATH "${BIN_DIRECTORY}/wait-for-it/:${PATH}"