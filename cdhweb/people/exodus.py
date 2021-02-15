"""Exodus script for people"""
import logging
from django.conf import settings

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q
from mezzanine.core.models import CONTENT_STATUS_PUBLISHED

from cdhweb.pages.exodus import convert_slug, get_wagtail_image, to_streamfield
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
            bio=to_streamfield(profile.bio)
        )
        # added as child of people landing page so slugs are correct
        people_landing.add_child(instance=profile_page)
        people_landing.save()
        # if the old profile wasn't published, unpublish the new one
        if profile.status != CONTENT_STATUS_PUBLISHED:
            profile_page.unpublish()

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
    - Removes all users with the is_staff flag set to False
    - Removes all users with the is_active flag set to False
    - Moves all remaining users into the Editors group

    Historically, many users were given the is_superuser flag to avoid a bug
    with Mezzanine permissions. In Wagtail, this is no longer necessary. In
    addition, there are two new default groups: Moderators and Editors.

    Users with is_staff or is_active set to False (preventing login) will be 
    deleted, since there's no need to keep them in the new system. User accounts
    are no longer associated with content (instead, People are).

    Note that you will still need to assign users to the Moderators group and
    turn on is_superuser manually after this runs. This can be done in console.
    """

    # get models and error if any aren't present - they should be since
    # wagtail's own migrations have already run
    User = get_user_model()
    moderators = Group.objects.get(name="Moderators")
    editors = Group.objects.get(name="Editors")

    # remove any groups that aren't editors or moderators - in cdhweb 2.x we
    # had an unused "Content Editor" group that should be deleted
    Group.objects.exclude(pk__in=(moderators.pk, editors.pk)).delete()

    # remove any users who had login disabled for some reason, except the
    # script user
    non_staff = 0
    for user in User.objects.filter(Q(is_staff=False) | Q(is_active=False)) \
                            .exclude(username=settings.SCRIPT_USERNAME):
        non_staff += 1
        logging.debug("removing user %s with is_staff=False" % user)
        user.delete()
    if non_staff:
        logging.info("removed %d non-staff users" % non_staff)

    # assign all remaining users to editors group; remove superuser.
    for user in User.objects.all():
        logging.debug("adding user %s to wagtail editors" % user)
        editors.user_set.add(user)
        user.is_superuser = False
        user.save()
    logging.info("total %d wagtail editors" % editors.user_set.count())
