Deploy Notes
============

2.2
---

- Adds an alumni page, parallel to current staff.  Existing profile pages
  for past staff should be republished.
- Fixes rich text page template to include page title as an H1.  Existing
  content with the title repeated will need to be edited.

2.1
---

- Resource names have been changed to store proper case in the database.
  Existing installations should update the three pre-populated items manually.
- Update local settings to turn on Google Analytics.

2.0
---

- Update default site in Django admin to match deployed site url
- Initialize admin and other users with createcasuser before running
  the data import.
- Import data from the previous version of the site (exported via Django
  dumpdata) using `python manage.py import_datav1 path_to_data.json`