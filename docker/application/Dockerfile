# syntax=docker/dockerfile:1.4

## -----
# Base backend
# On Debian, as prod is Ubuntu
FROM --platform=linux/x86_64 python:3.11-slim-bullseye as base

ENV PROJECT cdh-web
ENV ENVIRONMENT unknown
ENV APPLICATION_VERSION dev

WORKDIR /app

COPY requirements /app/requirements
COPY docker/requirements.txt docker/constraints.txt /app/docker/
COPY springkit_wagtail-dev.zip /app/springkit_wagtail-dev.zip

# RUN --mount=type=cache,target=/var/lib/apt/lists \
#     --mount=type=cache,target=/var/cache/apt \
#     rm -f /etc/apt/apt.conf.d/docker-clean && \
#     apt-get update -y && apt-get install -y  \
#     make nc

COPY requirements /app/requirements
COPY docker/requirements.txt docker/constraints.txt /app/docker/

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -U pip setuptools wheel && \
    pip3 install -r docker/requirements.txt && \
    pip3 install -r requirements/prod.txt

RUN adduser --system www -u 1000 && chown -R www /app


## -----
# NO production stage, as this app is run in Princeton's env, on bare-metal


## -----
# development stage
FROM base as app-dev

ENV DJANGO_SETTINGS_MODULE cdhweb.settings

ADD --chmod=755 https://github.com/mrako/wait-for/releases/download/v1.0.0/wait-for /usr/local/bin/

RUN --mount=type=cache,target=/var/lib/apt/lists \
    --mount=type=cache,target=/var/cache/apt \
    apt-get update -y && apt-get install --no-install-recommends -y \
    netcat

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r /app/requirements/dev.txt

# No COPY here as the local directory is volume-mounted in docker-compose

CMD ["/usr/local/bin/gunicorn", "--config", "/app/docker/gunicorn.py", "--reload", "cdhweb.wsgi" ]


## -----
# test stage
FROM base as app-test

ENV DJANGO_SETTINGS_MODULE app.settings.test

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r /app/requirements/test.txt

COPY ./ ./
# TODO: FRONTEND
# COPY --link --from=frontend /app/core/static /app/core/static
# COPY --link --from=frontend /app/core/templates /app/core/templates

CMD ["/bin/sh", "/app/test.sh"]


## -----
# Huey stage
FROM app as tasks
CMD ["python", "/app/manage.py",  "run_huey", "--huey-verbose"]

FROM app-dev as tasks-dev
CMD ["python", "/app/manage.py",  "run_huey", "--huey-verbose"]
