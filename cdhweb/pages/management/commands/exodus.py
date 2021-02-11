"""Convert mezzanine-based pages to wagtail page models."""
import filecmp
import glob
import json
import logging
import os
import os.path
import shutil
import warnings
from collections import defaultdict

from django.conf import settings
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand, CommandParser
from django.db.models import Q
from django.test import override_settings
from mezzanine.core.models import CONTENT_STATUS_PUBLISHED
from mezzanine.pages.models import Page as MezzaninePage
from wagtail.core.models import Collection, Page, Site, get_root_collection_id
from wagtail.images.models import Image

from cdhweb.pages.exodus import (convert_slug, create_contentpage,
                                 create_homepage, create_landingpage,
                                 create_link_page, form_pages,
                                 get_wagtail_image)
from cdhweb.pages.models import ContentPage, HomePage
from cdhweb.people.exodus import people_exodus, user_group_exodus
from cdhweb.people.models import PeopleLandingPage
from cdhweb.projects.exodus import project_exodus
from cdhweb.projects.models import ProjectsLinkPage

# log levels as integers for verbosity option
LOG_LEVELS = {
    0: logging.ERROR,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG
}


class Command(BaseCommand):
    help = __file__.__doc__

    # list to track migrated mezzanine pages by pk
    migrated = []

    # cached collections used for migrated media
    collections = {
        # get root collection so we can add children to it
        'root': Collection.objects.get(pk=get_root_collection_id())
    }

    def add_arguments(self, parser: CommandParser) -> None:
        # skip feature detection if requested (faster image loading)
        parser.add_argument(
            "--skip-feature-detection", "-s", action="store_true",
            help="Skip image feature detection with OpenCV"
        )

    def handle(self, *args, **options):
        """Create Wagtail pages for all extant Mezzanine pages."""
        # set up logging based on verbosity; ignore most low-level image logs
        # and raise UserWarnings from image handling as errors to log them
        logging.basicConfig(level=LOG_LEVELS[options["verbosity"]])
        logging.getLogger("PIL").setLevel(logging.WARNING)
        warnings.simplefilter(action="error", category=UserWarning)

        # clear out wagtail pages for idempotency
        Page.objects.filter(depth__gt=2).delete()

        # convert media images to wagtail images; detect features by default
        with override_settings(WAGTAILIMAGES_FEATURE_DETECTION_ENABLED=not options["skip_feature_detection"]):
            self.image_exodus()

        # create the new homepage
        try:
            old_homepage = MezzaninePage.objects.get(slug="/")
            homepage = create_homepage(old_homepage)
            # mark home page as migrated
            self.migrated.append(old_homepage.pk)
        # in some situations (e.g. fixture loading) there's no homepage
        except MezzaninePage.DoesNotExist:
            old_homepage = None
            homepage = HomePage(
                title="The Center for Digital Humanities at Princeton",
                seo_title="The Center for Digital Humanities at Princeton",
                slug="",
            )
        root = Page.objects.get(depth=1)
        root.add_child(instance=homepage)
        root.save()

        # point the default site at the new homepage and delete any others.
        # if they are deleted prior to switching site.root_page, the site will
        # also be deleted in a cascade, which we don't want
        site = Site.objects.get()
        site.root_page = homepage
        site.save()
        Page.objects.filter(depth=2).exclude(pk=homepage.pk).delete()

        # create a LinkPage to serve as the projects/ root (project list page)
        try:
            old_projects = MezzaninePage.objects.get(slug="projects")
            projects = ProjectsLinkPage(
                title=old_projects.title,
                link_url=old_projects.slug
            )
            homepage.add_child(instance=projects)
            homepage.save()
            self.migrated.append(old_projects.pk)
        except MezzaninePage.DoesNotExist:
            projects = None

        # create a dummy top-level events/ page for event pages to go under
        if MezzaninePage.objects.filter(slug="events").exists():
            events = ContentPage(
                title="Events",
                slug="events",
                seo_title="Events"
            )
            homepage.add_child(instance=events)
            homepage.save()
            # mark events content page as migrated
            self.migrated.append(
                MezzaninePage.objects.get(slug='events').pk)
        else:
            events = None

        # manually migrate the top-level people/ page to a special subtype
        try:
            old_people = MezzaninePage.objects.get(slug="people")
            people = PeopleLandingPage(
                title=old_people.title,
                tagline=old_people.landingpage.tagline,
                header_image=get_wagtail_image(old_people.landingpage.image),
                slug=convert_slug(old_people.slug),
                seo_title=old_people._meta_title or old_people.title,
                body=json.dumps([{
                    "type": "migrated",
                    "value": old_people.landingpage.content,
                }]),
                search_description=old_people.description,
            )
            homepage.add_child(instance=people)
            homepage.save()
            # mark as migrated
            self.migrated.append(old_people.pk)
        except MezzaninePage.DoesNotExist:
            people = None

        # migrate children of homepage
        if old_homepage:
            for page in old_homepage.children.all():
                self.migrate_pages(page, homepage)

        # special cases
        # - migrate event pages but specify new events page as parent
        if events:
            event_pages = MezzaninePage.objects \
                .filter(Q(slug__startswith="events/") | Q(slug="year-of-data"))
            for page in event_pages:
                self.migrate_pages(page, events)

        # migrate people pages as link pages
        if people:
            people_pages = MezzaninePage.objects \
                .filter(slug__startswith="people/").order_by('-slug')
            for page in people_pages:
                if page.pk not in self.migrated:
                    create_link_page(page, people)
                    self.migrated.append(page.pk)

        # migrate project pages
        if projects:
            # old landing page at projects/about
            try:
                old_projects_landing = MezzaninePage.objects.get(
                    slug="projects/about")
                projects_landing = create_landingpage(old_projects_landing)
                projects.add_child(instance=projects_landing)
                projects.save()
                self.migrated.append(old_projects_landing.pk)
            except MezzaninePage.DoesNotExist:
                pass

            # project list pages become link pages
            project_pages = MezzaninePage.objects \
                .filter(Q(slug__startswith="projects")).order_by('-slug')
            for page in project_pages:
                if page.pk not in self.migrated:
                    create_link_page(page, projects)
                    self.migrated.append(page.pk)

        # migrate all remaining pages, starting with pages with no parent
        # (i.e., top level pages)
        for page in MezzaninePage.objects.filter(parent__isnull=True):
            self.migrate_pages(page, homepage)

        # special cases — consult/co-sponsor form
        form_pages()

        # profiles, people
        people_exodus()

        # projects, memberships, grants, roles
        project_exodus()

        # report on unmigrated pages
        unmigrated = MezzaninePage.objects.exclude(
            pk__in=self.migrated)
        if unmigrated.count() == 0:
            logging.info("all mezzanine pages migrated")
        else:
            logging.warning("%d unmigrated mezzanine pages" %
                            unmigrated.count())
        for page in unmigrated:
            print('\t%s — slug/url %s)' % (page, page.slug))

        # delete mezzanine pages here? (but keep for testing migration)

    def get_collection(self, name):
        # if we don't already have this collection, get it
        if name not in self.collections:
            # try to get it if it already exists
            coll = Collection.objects.filter(name=name).first()
            # otherwise, create it
            if not coll:
                coll = Collection(name=name)
                self.collections['root'].add_child(instance=coll)
                self.collections['root'].save()

            self.collections[name] = coll

        return self.collections[name]

    def migrate_pages(self, page, parent):
        """Recursively convert a mezzanine page and all its descendants
        to Wagtail pages with the same hierarchy.

        :params page: mezzanine page to convert
        :params parent: wagtail page the new page should be added to
        """

        # if a page has already been migrated, skip it
        if page.pk in self.migrated:
            return

        # create the new version of the page according to page type
        if hasattr(page, "landingpage"):
            new_page = create_landingpage(page)
        else:
            # treat everything else as page / richtexpage
            if hasattr(page, "link"):
                logging.warning(
                    "converting link page to content page %s " % page)
                # TODO: adapt new create_link_page method for these links
            new_page = create_contentpage(page)

        parent.add_child(instance=new_page)
        parent.save()

        # set publication status
        if page.status != CONTENT_STATUS_PUBLISHED:
            new_page.unpublish()

        # add to list of migrated pages
        self.migrated.append(page.pk)

        # recursively create and add new versions of all this page's children
        for child in page.children.all():
            self.migrate_pages(child, new_page)

    def get_media_files(self):
        # wagtail images support: GIF, JPEG, PNG, WEBP
        imgfile_path = '%s/**/*.*' % settings.MEDIA_ROOT
        # get filenames for all uploaded files
        filenames = glob.glob(imgfile_path, recursive=True)
        # aggregate files by basename to identify files with the same
        # name in different locations
        unique_filenames = defaultdict(list)
        for path in filenames:
            unique_filenames[os.path.basename(path)].append(path)

        # check files with the same name in multiple locations
        for key, val in unique_filenames.items():
            if len(val) > 1:
                samefile = filecmp.cmp(val[0], val[1], shallow=False)
                # if the files are the same
                if samefile:
                    # keep the first one and remove the others from the
                    # list of files to be migrated
                    extra_copies = val[1:]

                # if not all the same, identify the largest
                # (all are variant/cropped versions of the same image)
                else:
                    largest_file = None
                    largest_size = 0
                    for filepath in val:
                        size = os.stat(filepath).st_size
                        if size > largest_size:
                            largest_size = size
                            largest_file = filepath

                    extra_copies = [f for f in val if f != largest_file]

                # remove duplicate and variant images that
                # will not be imported into wagtail
                for extra_copy in extra_copies:
                    filenames.remove(extra_copy)

        return filenames

    def image_exodus(self):
        # generate wagtail images for all uploaded media

        # mezzanine/filebrowser_safe doesn't seem to have useful objects
        # or track metadata, so just import from the filesystem

        # delete all images prior to run
        # (clear out past migration attempts)
        # NOTE we leave collections alone and don't delete them between runs;
        # doing so seems to corrupt the page/collection tree
        Image.objects.all().delete()

        # also delete any wagtail image files, since they are not deleted
        # by removing the objects
        shutil.rmtree('%s/images' % settings.MEDIA_ROOT, ignore_errors=True)
        shutil.rmtree('%s/original_images' %
                      settings.MEDIA_ROOT, ignore_errors=True)

        # get media filenames to migrate, with duplicates filtered out
        media_filenames = self.get_media_files()

        for imgpath in media_filenames:
            extension = os.path.splitext(imgpath)[1]
            # skip unsupported files based on file extension
            # NOTE: leaving this here in case we want to handle
            # documents the same way
            if extension in ['.pdf', '.svg', '.docx']:
                continue

            # if image is in a subdirectory under uploads (e.g. projects, blog)
            # add it to a collection with that name
            relative_path = os.path.dirname(imgpath) \
                .replace(os.path.join(settings.MEDIA_ROOT, 'uploads'), '')

            # there are two variants of Slavic DH, one with and one
            # without a space; remove the space so they'll be in one collection
            basedir = relative_path.strip('/').split('/')[0].replace(' ', '')
            collection = None
            if basedir:
                collection = self.get_collection(basedir)

            with open(imgpath, 'rb') as imgfilehandle:
                title = os.path.basename(imgpath)
                # passing collection=None errors, so
                # only specify collection option when we have one
                extra_opts = {}
                if collection:
                    extra_opts['collection'] = collection
                try:
                    Image.objects.create(
                        title=title,
                        file=ImageFile(imgfilehandle, name=title),
                        **extra_opts)
                except Exception as err:
                    # seems to mean that height/width calculation failed
                    # (usually non-images)
                    logging.warning("%s: %s" % (imgpath, err))
