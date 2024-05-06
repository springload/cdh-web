# syntax=docker/dockerfile:1.4

## Frontend TODO once Springload approach added
# # frontend assets
# FROM node:20-alpine as frontend

# RUN apk add --update git

# WORKDIR /app

# # Install packages
# COPY package.json package-lock.json /app/
# RUN --mount=type=cache,target=/root/.npm NPM_CACHE_FOLDER=/root/.npm \
#     npm ci

# # Copy config/build files
# COPY webpack.config.js webpack.fix-django-paths.js tsconfig.json /app/
# COPY core/static_src /app/core/static_src
# COPY core/templates_src /app/core/templates_src

# RUN npm run build

# CMD ["npm", "run build"]


## -----
# Base backend
# On Debian, as their prod is Ubuntu
FROM --platform=linux/x86_64 python:3.11-slim-bullseye as base

ENV PROJECT cdh-web
ENV ENVIRONMENT unknown
ENV APPLICATION_VERSION dev

WORKDIR /app

COPY requirements /app/requirements
COPY docker/requirements.txt docker/constraints.txt /app/docker/

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

# TODO: Frontend: Remove npm install once deps are built without compressor
RUN --mount=type=cache,target=/var/lib/apt/lists \
    --mount=type=cache,target=/var/cache/apt \
    apt-get update -y && apt-get install --no-install-recommends -y \
    netcat npm

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r /app/requirements/dev.txt \
    npm install

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
