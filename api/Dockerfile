FROM python:3.10-slim as build

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl gcc python3-dev libssl-dev gettext locales git libpq-dev \
    && echo ru_RU.UTF-8 UTF-8 >> /etc/locale.gen \
    && locale-gen && apt-get autoclean && apt-get autoremove --yes && rm -rf /var/lib/{apt,dpkg,cache,log}/

# install PDM
RUN pip install -U pip setuptools wheel
RUN pip install pdm


WORKDIR /app
# copy meta
COPY pyproject.toml pdm.lock /app/

# install deps and project itself
RUN pdm install --prod --no-lock --no-editable

# # rm compiled stuff
# RUN find __pypackages__ -name '__pycache__' -exec rm -Rf {} +

FROM python:3.10-slim


RUN apt-get update && \
    apt-get install -y --no-install-recommends libssl-dev gettext locales libpq-dev netcat-openbsd && \
    echo ru_RU.UTF-8 UTF-8 >> /etc/locale.gen && \
    locale-gen && apt-get autoclean && apt-get autoremove --yes && rm -rf /var/lib/{apt,dpkg,cache,log}/

# logs stuff
ENV PYTHONUNBUFFERED=1

WORKDIR /app
ENV PYTHONPATH=/app:/opt/dist/lib
ENV PATH="/opt/dist/bin:$PATH"
COPY --from=build /app/__pypackages__/3.10/ /opt/dist/

COPY . .
EXPOSE 80
CMD gunicorn --chdir /app tasks_api.wsgi:application -b :80 -w 4 --threads 8
ENTRYPOINT ["./entrypoint.sh"]
