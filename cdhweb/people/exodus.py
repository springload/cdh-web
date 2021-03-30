"""Exodus script for people"""
import logging
from django.conf import settings

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q
from mezzanine.core.models import CONTENT_STATUS_PUBLISHED

from cdhweb.pages.exodus import convert_slug, exodize_attachments, exodize_history, get_wagtail_image, to_streamfield
from cdhweb.people.models import OldProfile, PeopleLandingPage, Person, Profile


def people_exodus():
    """Exodize all existing Profiles to new Profile model, and use old Profile
    images to update People."""
    # all the fields on Profile that moved to Person will have been handled
    # by django migrations; we just need to create new Page models
    people_landing = PeopleLandingPage.objects.first()
    if not people_landing:
        return
    # only create profiles if there's actually text in the old one
    for profile in OldProfile.objects.exclude(bio=""):
        person = Person.objects.get(user=profile.user)
        profile_page = Profile(
            person=person,
            title=profile.title,
            slug=convert_slug(profile.slug),
            image=get_wagtail_image(profile.image) if profile.image else get_wagtail_image(
                profile.thumb) if profile.thumb else None,
            education=profile.education,
            body=to_streamfield(profile.bio),
            search_description=profile.description,
        )

        # added as child of people landing page so slugs are correct
        people_landing.add_child(instance=profile_page)
        people_landing.save(log_action=False)

        # if the old profile wasn't published, unpublish the new one
        if profile.status != CONTENT_STATUS_PUBLISHED:
            profile_page.unpublish(log_action=False)

        # set publication dates
        profile_page.first_published_at = profile.publish_date
        profile_page.last_published_at = profile.updated
        profile_page.save(log_action=False)

        # move attachments
        exodize_attachments(profile, profile_page)
        exodize_history(profile, profile_page)

    # for people with profile, set larger image as wagtail image for person
    for profile in OldProfile.objects.filter(user__person__isnull=False):
        person = Person.objects.get(user=profile.user)
        if profile.image:
            person.image = get_wagtail_image(profile.image)
            person.save()

        # if no large image but we do have thumbnail, use it as a fallback
        elif profile.thumb:
            person.image = get_wagtail_image(profile.thumb)
            person.save()


def user_group_exodus():
    """Convert groups from Mezzanine configuration to Wagtail configuration.

    - Removes any groups outside Wagtail default Moderators and Editors
    - Removes all users who have never logged in/made a change to the site
    - Moves all remaining users into the Moderators group
    - Marks any users without a current CDH position as inactive (no login)
    - Whitelists RSK and NB as superusers

    Historically, many users were given the is_superuser flag to avoid a bug
    with Mezzanine permissions. In Wagtail, this is no longer necessary. In
    addition, there are two new default groups: Moderators and Editors.

    This function moves everyone into the Moderators group, so that they are
    able to manage and publish all resources. If desired, some users may need
    to be later moved to the Editors group to de-escalate their permissions. 
    This can be accomplished via the Wagtail admin or in console; it needs to
    be done by a superuser.

    Users that have never logged in will be deleted, since they are not tied to
    any history or changes in the site. If a user account is connected to a
    Person that has an expired CDH position, that account will be marked as
    inactive to prevent logins.

    Note that, if desired, you may still need to give some users superuser after
    this has been run. This can be done via the `--admin` flag on `createcasuser`
    or via the django shell.
    """

    # get models and error if any aren't present - they should be since
    # wagtail's own migrations have already run
    User = get_user_model()
    moderators = Group.objects.get(name="Moderators")
    editors = Group.objects.get(name="Editors")

    # remove any groups that aren't editors or moderators - in cdhweb 2.x we
    # had an unused "Content Editor" group that should be deleted
    Group.objects.exclude(pk__in=(moderators.pk, editors.pk)).delete()

    # remove any users who have never logged in, except script user. this way
    # old accounts can still be associated with their changes/log entries
    no_actions = User.objects.filter(last_login__isnull=True) \
                             .exclude(username=settings.SCRIPT_USERNAME)
    logging.debug("removing %d users with no logins/changes" %
                  no_actions.count())
    no_actions.delete()

    # for anyone without a current CDH position, mark user account as inactive.
    # remove superuser permissions and add the user to the moderators group
    for user in User.objects.exclude(username=settings.SCRIPT_USERNAME):
        logging.debug("adding user %s to wagtail moderators" % user)
        moderators.user_set.add(user)
        user.is_superuser = False
        user.save()
        try:
            person = Person.objects.get(user=user)
            if not person.current_title:
                logging.debug("marking user %s non-active" % user)
                user.is_active = False
                user.save()
        except Person.DoesNotExist:
            pass

    # whitelist rsk and nb as superusers for convenience
    for username in ["rkoeser", "nbudak"]:
        try:
            user = User.objects.get(username=username)
            logging.debug("marking user %s superuser" % user)
            user.is_superuser = True
            user.save()
        except User.DoesNotExist:
            pass

    logging.info("total %d wagtail moderators" % moderators.user_set.count())
