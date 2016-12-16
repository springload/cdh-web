# CDH Website Repo

[![Build Status](https://travis-ci.org/Princeton-CDH/cdh-web.svg?branch=develop)](https://travis-ci.org/Princeton-CDH/cdh-web)
[![codecov](https://codecov.io/gh/Princeton-CDH/cdh-web/branch/develop/graph/badge.svg)](https://codecov.io/gh/Princeton-CDH/cdh-web)
[![Code Health](https://landscape.io/github/Princeton-CDH/cdh-web/develop/landscape.svg?style=flat)](https://landscape.io/github/Princeton-CDH/cdh-web/develop)

## Overview
The purpose of this repo is to house the development files for the current version of the CDH Website,
including static files used in templates (**not** static/media).

Initial development of the site in 09/16 and 10/16 used [Mezzanine 4.2.0](mezzanine.jupo.org/docs/) running on [django 1.10](https://docs.djangoproject.com/en/1.10).

Mezzanine's "Mezzanine is just django" approach allowed the project to be easily created with a series of interlocking
applications developed to serve custom page types, as well as to add iCal support and feeds.

The website lives on the server cdh-web.princeton.edu (publicly aliased as digitalhumanities.princeton.edu).

+ cdhWebsite
  + Primary settings, local_settings.py held on server
+ eventspages
  + This app includes models for events, their publication pages, and the overall events page_processor
+ icalevents
  + This app provides an ical feed at /ical/<event number>
+ index
  + This app provides a page_processor for index.html and the base home page
+ projectpages
  + This app provides models for projects, project pages, and the project page boxes at /projects/
+ staffprofiles
	+ This app provides models for staff, their individual pages (not complete), and the staff director page_processor
+ static
	+ Static files included here, including copies of jQuery, fonts, and modified Bootstrap3 CSS
+ stocktemplate
	+ This app provides models for stockpages.
+ subscribe
  + This app provides models and views for subscribing to the listserv (which must still be approved with an OK email from
digitalhumanities@princeton.edu
+ templates
  + All template files, including blog/ includes/ and pages/, as well as templates in the main directory for displaybles, primarily project and event individual pages (staff pages to be added)


## Development instructions

Initial setup and installation:

- recommended: create and activate a python 3.5 virtualenv
    `virtualenv cdhweb -p python3.5`
    `source cdhweb/bin/activate`

- pip install required python dependencies
    `pip install -r requirements.txt`
    `pip install -r dev-requirements.txt`

- copy sample local settings and configure for your environment
    `cp cdhweb/local_settings.py.sample cdhweb/local_settings.py`

- install & configure [git post-commit hook](https://gist.github.com/rlskoeser/ffa7bb517eeca54e63f3015a9f89d917) for Asana integration


## Unit Testing

Unit tests are written with [py.test](http://doc.pytest.org/) but use Django fixture loading and convenience
testing methods when that makes things easier.  To run them, first install
development requirements:
```
pip install -r dev-requirements.txt
```

Run tests using py.test:
```
py.test
```
