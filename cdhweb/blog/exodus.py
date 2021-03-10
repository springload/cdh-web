"""Exodus script for blog posts."""
import logging

from mezzanine.core.models import CONTENT_STATUS_PUBLISHED

from cdhweb.people.models import Person
from cdhweb.pages.exodus import convert_slug, get_wagtail_image, to_streamfield
from cdhweb.blog.models import BlogPost, BlogLinkPage, OldBlogPost, Author


def blog_exodus():
    """Exodize all blog models."""
    # get the top-level blog link page
    try:
        blog_link = BlogLinkPage.objects.get()
    except BlogLinkPage.DoesNotExist:
        logging.error("no blog link page; aborting blog exodus")
        return

    # fetch default blog post author ("CDH Staff" person)
    default_author = Person.objects.get_or_create(first_name="CDH Staff")[0]

    # create new blog posts
    for post in OldBlogPost.objects.all():
        logging.debug("found mezzanine blogpost %s" % post)

        # create page
        post_page = BlogPost(
            title=post.title,
            slug=convert_slug(post.slug),
            featured=post.is_featured,
            search_description=post.description,
            body=to_streamfield(post.content),
            featured_image=get_wagtail_image(post.featured_image)
        )

        # add it as a child of blog landing page so slugs are correct
        blog_link.add_child(instance=post_page)
        blog_link.save()

        # if the old post wasn't published, unpublish the new one
        if post.status != CONTENT_STATUS_PUBLISHED:
            post_page.unpublish()

        # set publication date
        post_page.first_published_at = post.publish_date
        post_page.save()

        # transfer authors
        for user in post.users.all():
            person = Person.objects.get(user=user)
            Author.objects.create(person=person, post=post_page)

        # if no author, use default
        if not post.users.exists():
            Author.objects.create(person=default_author, post=post_page)

        # NOTE no tags to migrate
        # TODO transfer attachments
