Deploy Notes
============

2.8
---

- A new "DH Working Groups" page should be created under the Projects page in
  mezzanine with its slug set to `/projects/working-groups` to enable the new
  DH Working Groups page.
- Any Working Groups that were created as pages (not projects) can be deleted,
  and their content can be moved into a new Project.
- Any Working Groups that were assigned the "working group" grant type can have
  this removed, and the grant type can be deleted.
- Any non-R&D Staff Projects that were assigned the "staff r&d" grant type can
  have this changed to "Staff Projects", and the grant type can be deleted.

2.7
---

- The "Faculty Affiliates" page has changed to show both Faculty and Staff, and
  thus its title and content should be updated accordingly in Mezzanine.

2.6
---

- Adds a cosponsorship request form embed template similar to the consult form.
  A `RichTextPage` needs to be created with its url set to `/events/cosponsor`
  in order to automatically embed the form.
- The events page needs to be recreated as a `RichTextPage` to support adding
  text at the top of the page. To disable the text at the top, enter two non-
  breaking spaces in the text field. Make sure the url remains `/events`.

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