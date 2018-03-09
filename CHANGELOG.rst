CHANGELOG
=========

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
* Multiple design fixes and improvements
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

