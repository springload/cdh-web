"""Exodus script for people"""

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
