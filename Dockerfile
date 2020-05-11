FROM python:3.7-slim

ENV PIP_NO_CACHE_DIR yes
ENV LD_LIBRARY_PATH /usr/local/lib

RUN \
  apt-get update -yqq && \
  apt-get install -yqq libaio1 && \
  pip install --upgrade pip pipenv

COPY Pipfile* /
RUN pipenv install --deploy --system --ignore-pipfile
COPY lib/* /usr/local/lib/
COPY dw_lookup /dw_lookup

ENTRYPOINT ["gunicorn"]
CMD ["-b", "0.0.0.0", "dw_lookup.app:app"]
