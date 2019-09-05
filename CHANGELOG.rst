CHANGELOG
=========

2.6
---

* As a Content Editor, I want a visual indicator when I'm viewing a page that is not yet published so that I can distinguish between published and unpublished content.
* As a Content Editor, I want to add text content to the events page so that I can add context to the list of events.
* display grant history on project pages
* add a 'status override' flag to always show grant memberships as current or past
* add a template for embedding the event cosponsorship form
* add a visual indicator when viewing a draft page
* bugfix: second-level navigation pages don't respect "show in nav" setting
* bugfix: links in lists don't get body link style
* chore: adjust content priority values in sitemap
* accessibility: make main navigation usable with a keyboard
* accessibility: make "skip to" links visible when focused via keyboard
* accessibility: add text-shadow to landing page headings
* accessibility: add empty alt for event featured images
* accessibility: add link titles for event cards

2.5
---

* bugfix: event card doesn't display names from person, only from profile
* Document installation and use of timezone files for MariaDB/MySQL
* Update social media links
* Add links to profile urls for project alums


2.4.3
-----

* bugfix: blogpost RSS feed does not respect draft status
* Configure admin search fields for projects, grants, and blog posts
* Display event attendance in admin list view

2.4.2
-----

* Order faculty affiliates by last name
* Use png instead of svg for social media / opengraph preview icon images,
  since svg is not supported
* Tweak profile card display logic for faculty fellowship
* Include Postgraduate Research Assistants on the postdocs page
* Configure admin search for position list
* Use book icon for reading group, location marker for travel grants

2.4.1
-----

* bugfix: blog post list author and event detail speaker link to unpublished
  profiles
* Require Pillow v 5.2
* Style fix for h2 padding on project and event cards

2.4
---

Accessibility updates and new features to display projects in different groupings
with indicators for projects build by CDH and those with live websites, and
multiple pages to display current and past people affiliated with CDH.

This release includes numerous design fixes and improvements.

Features
~~~~~~~~
* As a user, I want to easily read and use the main site navigation so I can get to the content that interests me.
* As a user, I want to traverse the main navigation using a keyboard so that I can access site content more easily.
* As a user, I want to see current, staff, and past projects so I can easily see which projects are active and know more about staff research.
* As a user, I want to see which projects were developed by CDH so that I can get a better sense of CDH involvement in the projects.
* As a user, I want to see which projects in the project list have a live website so that I can see which projects are accessible and get to them.
* As a user, I want to easily find project URLs so I can get to the actual websites and see projects that are live.
* As a user, I want to see CDH staff, postdocs, and students on separate pages so I can see current and past people associated with CDH grouped by category.
* As a user, I want to see photos and brief details for faculty affiliates and executive committee members so I can see the faces of people associated with CDH.
* As a user, I want to see upcoming and past speakers at CDH events so I can see what kind of scholars CDH is bringing to campus.
* As a user, I want to see recent blog posts by a CDH staff member or other affiliate on their profile page so that I can read more about their work.
* As a user, I want to easily find the subscribe link so I know there is a newsletter and how to subscribe to it.
* As an admin, I want to edit text content on the home page so that I can manage and update brief introductory content for site visitors.
* As a content admin, I want to add and edit text to be included on people pages so that I can describe faculty affiliation or other groups.
* As a content admin, I want to document event attendance in the database so that it can be tracked and reported with other event information.

Chores, fixes, and other items
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* bugfix: HTML entity rendering issues for blog post and page preview text
* bugfix: home page carousel now respects draft status
* Embedded consultation request form on user-editable page
* Customize XML Sitemap with last modification dates for all content
* Display phone number and office location on profile detail page
* Use CDH icons for related page attachment cards and open graph/twitter previews
* Set up automated accessibility testing with pa11y-ci
* Removed data import script written for migration from CDH web 1.0
* Upgraded to Mezzanine 4.3

2.3.1
-----

Sets a null href attribute on carousel links to prevent reloading the page but keep them accessible to screen readers.

2.3
---

* As a Content Editor, I want my rich text editor preview to match the way the content will display on the site so that I don't have to check the published version myself.
* As a Content Editor, I should only be able to use supported formatting and tags when I edit site content so that the CDH has a uniform web presence.
* As a Content Editor, I want to designate blog posts as featured so I can highlight their importance.
* As a user, I want to see featured updates on the homepage so I can see what's going on at the CDH.

Upgrade tinyMCE to v4.7.9.

2.2.2
-----

Downgrade Django to 1.10.x (and latest released version of Mezzanine)
to avoid a Django compatibility issue with filebrowser_safe.

2.2.1
-----

Minor Sphinx documentation and README cleanup.

2.2
---

* As a user, I want to see past CDH positions on a staff member profile page so I can learn about a person's history with CDH.
* As a user I want to view a list of alumni so I can get learn about people who have worked with CDH in the past.
* As a user, I want to see details about CDH alumni so I can learn about their past work at CDH and where they are now.
* Upcoming events page now includes 6 most recent past events
* Upgrade to Django 1.11.x
* bug fix: home page doesn't display any message when there are no upcoming events
* bug fix: events page is broken when there are no upcoming events
* bug fix: events with different starting and ending months error on display
* bug fix: non-CDH address display on event detail page repeats information
* bug fix: allow adding speakers to events pages without creating a profile
* bug fix: people with multiple positions are listed multiple times on the staff page
* Multiple design fixes and improvements'

  * converted from Neat grid to CSS Grid for main grid and footer
  * fixed broken image reference for events with no detail image
  * mobile footer formatting and mobile main navigation menu
  * Typography link style fixes
  * Main menu navigation (LM viewport) now provides submenu links on hover
  * Improved navigation menu style for moving between events pages, staff and alumni pages
  * Improvements to event card, project detail page, profile page, content pages

2.1
---

* As a content editor, I want to associate people with projects more efficiently so I don't have to enter repeating information.
* bug fix: Resource links on user profile page don't work
* bug fix: People with multiple positions are listed multiple times on the staff page
* bug fix: Event urls now honor year/month and event slugs can be repeated
* Basic twitter/opengraph metadata now included in page headers
* robots.txt now managed by the application; includes path to sitemap.xml
* favicon now managed by the application; includes dev/test icon
* Many improvements and clean up in design implementation

2.0
---

**CDH web 2.0 is a completely new implementation of the functionality in the
previous version, with a restructured database and site templates based on
bourbon+neat rather than bootstrap.**

Profiles
~~~~~~~~

* As a user I want to view a list of staff members so I can get an idea of the people who work at the CDH.
* As a user, I want to see details about a staff member so I can learn about their role, research interests, and how to contact them.
* As an admin, I want to create and edit staff profiles so I can publish information about staff research and roles.
* As an admin, I want user information and titles automatically populated so I don't have to manually enter it.

Events
~~~~~~

* As a user I want to view a list of upcoming events so that I can find and attend events that interest me.
* As a user, I want to view event details so I can decide if I'm interested and know when and where to attend.
* As a user, I want to view previous events by semester so that I can get a sense of event and workshop offerings.
* As a user, I want to download event information as ical so I can add it to my personal calendar.
* As a content editor, I want to create and edit event types so I can categorize kinds of events.
* As a content editor, I want to create and edit event locations so that I can enter them once and have them displayed consistently across the site.
* As a content editor, I want to create and edit events so that I can publicize workshops, lectures, or other events.

Projects
~~~~~~~~

* As a user I want to see a list of current projects so I can learn more about the work of CDH.
* As a user, I want to view sponsored project details so I can read about project goals, progress, and contributors.
* As an admin, I want to associate urls for other resources with projects so that I can provide links to materials related to projects.
* As an admin, I want to create and edit project roles and associate people as members of projects so that I can document project contributors.
* As an admin, I want to create and edit grant types and associate grants with projects, so that I can document when and which kinds of grants a project received from CDH.
* As an admin user, I want to create and edit project pages so that I can publish information about sponsored projects.

Blog
~~~~

* As a user, I want to view previous blog posts by year and month so that I can read past updates.
* As a user, I want to subscribe to a blog post feed so I can read CDH updates in the feed reader of my choosing.
* As a user, I want to view blog posts so that I can read updates about CDH and its work.
* As a user, I want to browse a paginated list of blog posts so that I can find and read older updates about CDH and its work.
* As a content editor, I want to create and edit blog posts so that I can share updates about CDH and its work.
* As a content editor, I want to associate an author other than myself with a blog post so that I can indicate who wrote the content.
* As a content editor, I want to associate one or more authors with a blog post so that I can document everyone who contributed to the content.

Other Content
~~~~~~~~~~~~~

* As a user, I want to navigate using the header or footer menus, so that I can find the content I'm looking for.
* As a user I want to view upcoming events and highlighted projects on the homepage so I can get a sense of the CDH and its activities.
* As a user, I want to view content pages so that I can read materials that interest me.
* As a user, I want to view and download files associated with pages on the site so that I can access other materials related to the content.
* As an admin, I want to upload files and media and associate them with other content so that I can share files and other non-web content with users.
* As an admin I want to edit and create resource types so I can determine what kind of links and resources can be associated with people and projects.
* As an admin, I want to manage links in the header so that I can update navigation when the site changes.
* As an admin, I want to create and manage landing pages and other content pages so that I can publish top-level and other content pages.
* As an admin, I want to manage links in the footer so I can update site navigation when content changes.

Import
~~~~~~
* As an admin, I want an import of content from the previous version of the site so that all the information available on the old site is migrated to the new version.

