CDH Website
===========

.. sphinx-start-marker-do-not-remove

.. image:: https://travis-ci.org/Princeton-CDH/cdh-web.svg?branch=develop
   :target: https://travis-ci.org/Princeton-CDH/cdh-web
   :alt: Build status

.. image:: https://landscape.io/github/Princeton-CDH/cdh-web/develop/landscape.svg?style=flat
  :target: https://landscape.io/github/Princeton-CDH/cdh-web/develop
  :alt: Code Health

.. image:: https://codecov.io/gh/Princeton-CDH/cdh-web/branch/develop/graph/badge.svg
   :target: https://codecov.io/gh/Princeton-CDH/cdh-web
   :alt: Code coverage

.. image:: https://requires.io/github/Princeton-CDH/cdh-web/requirements.svg?branch=develop
   :target: https://requires.io/github/Princeton-CDH/cdh-web/requirements/?branch=develop
   :alt: Requirements Status


`cdhweb` is a Django+Mezzanine application that powers the CDH website
with custom models for people, events, and projects.

View `software and architecture documentation <https://princeton-cdh.github.io/cdh-web/>`_
for the current release.

This repository uses `git-flow <https://github.com/nvie/gitflow>`_ conventions; master
contains the most recent release, and work in progress will be on the develop branch.
Pull requests should be made against develop.



Development instructions
------------------------

Initial setup and installation:

- recommended: create and activate a python 3.5 virtualenv::

    virtualenv cdhweb -p python3.5
    source cdhweb/bin/activate

- pip install required python dependencies::

    pip install -r requirements.txt
    pip install -r dev-requirements.txt

- copy sample local settings and configure for your environment::

    cp cdhweb/local_settings.py.sample cdhweb/local_settings.py

- download licensed fonts and install locally under /sitemedia/fonts/

- django-compressor dependencies: install `sass <http://sass-lang.com/install>`_
  for your operating system as appropriate. If you have Ruby gems installed,
  `gem install sass`. Also install `Node.js <https://nodejs.org/en/>`_ and `npm`.
  Globally install `postcss-cli` and `autoprefixer`, i.e.
  `npm -g postcss-cli autoprefixer`. You may need `sudo` for these operations.


Unit Testing
------------

Unit tests are written with `py.test <http://doc.pytest.org/>`_ but use
Django fixture loading and convenience testing methods when that makes
things easier.  To run them, first install development requirements::

  pip install -r dev-requirements.txt

Run tests using py.test::

  py.test

Documentation
~~~~~~~~~~~~~

Documentation is generated using `sphinx <http://www.sphinx-doc.org/>`__
To generate documentation, first install development requirements::

    pip install -r dev-requirements.txt

Then build the documentation using the customized make file in the `docs`
directory::

    cd sphinx-docs
    make html

When building documentation for a production release, use `make docs` to
update the published documentation on GitHub Pages.

