CDH Website
===========

.. sphinx-start-marker-do-not-remove

.. image:: https://github.com/Princeton-CDH/cdh-web/workflows/unit%20tests/badge.svg
   :target: https://github.com/Princeton-CDH/cdh-web/actions?query=workflow%3A%22unit+tests%22
   :alt: Unit test status

.. image:: https://codecov.io/gh/Princeton-CDH/cdh-web/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/Princeton-CDH/cdh-web
   :alt: Code coverage

.. image:: https://github.com/Princeton-CDH/cdh-web/workflows/dbdocs/badge.svg
    :target: https://dbdocs.io/princetoncdh/cdhweb
    :alt: dbdocs build

.. image:: https://percy.io/static/images/percy-badge.svg
    :target: https://percy.io/3201ecb4/cdh-web
    :alt: Visual regression tests

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: "code style Black"

.. image:: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
    :target: https://pycqa.github.io/isort/
    :alt: "imports: isort"

Python 3.11 / Django 4.2 / Node 18 / PostgreSQL 12
`cdhweb` is a Django+Wagtail application that powers the CDH website
with custom models for people, events, and projects.

View `software and architecture documentation <https://princeton-cdh.github.io/cdh-web/>`_
for the current release.

This repository uses `git-flow <https://github.com/nvie/gitflow>`_ conventions; **main**
contains the most recent release, and work in progress will be on the **develop** branch.
Pull requests should be made against **develop**.


Development instructions
------------------------

Bare-metal
~~~~~~~~~~

Initial setup and installation:

- Recommended: create and activate a python 3.9 virtualenv::

    virtualenv cdhweb -p python3.9
    source cdhweb/bin/activate

- Use pip to install required python dependencies.  To install production
  dependencies only::

    pip install -r requirements.txt

  To install all development requirements::

    pip install -r requirements/dev.txt

- Install django-compressor dependencies::

    npm install

- Copy sample local settings and configure for your environment::

    cp cdhweb/settings/local_settings.py.sample cdhweb/settings/local_settings.py

You must add a ``SECRET_KEY`` value in your local settings.

- Download licensed fonts and install locally under /sitemedia/fonts/

- Install OpenCV dependencies (if necessary) for `wagtail image feature detection <https://docs.wagtail.io/en/stable/advanced_topics/images/feature_detection.html>`_

Docker (Springload)
~~~~~~~~~~~~~~~~~~~

- Download the **database**, **media dump** and **fonts** from https://drive.google.com/drive/u/0/folders/1B7qObEuO6sYJhVyE23RP8Tf0IbFCLlMf
- Copy the database dump into `docker/database`
- Extract the media into `media`

    tar -xvzf path_to_file.tar.gz -C media

- Move the font files into `static_src/fonts`
- Copy cdhweb/settings/local_settings.py.docker-sample to cdhweb/settings/local_settings.py
- Run `docker-compose up`

Frontend (Springload)
~~~~~~~~~~~~~~~~~~~~~

The frontend uses webpack and npm.

First, make sure you're using the correct node version:

  nvm use

If it tells you to install a new version, do so. Then run ``nvm use`` again.

Install dependencies:

  npm install

Then to run the site in development mode locally:

  npm start

Setup pre-commit hooks
~~~~~~~~~~~~~~~~~~~~~~

If you plan to contribute to this repository, please run the following command::

    pre-commit install

This will add a pre-commit hook to automatically style your python code with `black <https://github.com/psf/black>`_.

Because these styling conventions were instituted after multiple releases of
development on this project, ``git blame`` may not reflect the true author
of a given line. In order to see a more accurate ``git blame`` execute the
following command::

    git blame <FILE> --ignore-revs-file .git-blame-ignore-revs

  Or configure your git to always ignore styling revision commits:

    git config blame.ignoreRevsFile .git-blame-ignore-revs

Unit Testing
------------

Unit tests are written with `py.test <http://doc.pytest.org/>`_ but use
Django fixture loading and convenience testing methods when that makes
things easier.  To run them, first install test requirements (these are
included in dev)::

  pip install -r requirements/test.txt

Run tests using py.test::

  py.test

Visual Testing
--------------

Visual regression tests are written using the Python bindings for Selenium,
and DOM snapshots are uploaded to `Percy <https://percy.io/>`_. They run in CI
on pushes or pull requests to the `develop` branch.

Before visual tests are run, the CI build will execute::

  python manage.py create_test_site

Which uses existing pytest fixtures to populate the database with content
approximating a real website in order to execute the tests. It will then run::

  npm run test:visual

Which starts a Django development server and calls the `ci/visual_tests.py`
script to upload DOM snapshots to Percy for regression analysis.

You can use both of these commands locally if you need to accomplish either of
these tasks. You will need to have the dependencies in `requirements/test.txt`
installed, and set `PERCY_TOKEN` in your shell environment.

Documentation
~~~~~~~~~~~~~

Documentation is generated using `sphinx <http://www.sphinx-doc.org/>`__
To generate documentation, first install development requirements::

    pip install -r requirements/dev.txt

Then build the documentation using the customized make file in the `docs`
directory::

    cd sphinx-docs
    make html

When building documentation for a production release, use `make docs` to
update the published documentation on GitHub Pages.

On every commit, GitHub Actions will generate and then publish a database diagram to `dbdocs @ princetoncdh/cdh-web <https://dbdocs.io/princetoncdh/cdh-web>`_. But to generate locally, install and log into dbdocs. Then run::

    python manage.py dbml > cdhweb.dbml
    npx dbdocs build cdhweb.dbml --project cdhweb

License
-------
This project is licensed under the `Apache 2.0 License <https://github.com/Princeton-CDH/cdh-web/blob/main/LICENSE>`_.

©2023 Trustees of Princeton University.  Permission granted via
Princeton Docket #20-2634 for distribution online under a standard Open Source
license. Ownership rights transferred to Rebecca Koeser provided software
is distributed online via open source.