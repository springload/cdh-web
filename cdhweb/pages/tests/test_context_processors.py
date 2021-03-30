from wagtail.core.models import Page

import pytest

from cdhweb.pages.context_processors import page_intro
from cdhweb.pages.models import LinkPage, PageIntro


@pytest.mark.django_db
def test_page_intro(rf):
    root = Page.objects.get(title="Root")
    link_page = LinkPage(title='Students', link_url='people/students')
    root.add_child(instance=link_page)
    intro = PageIntro.objects.create(
        page=link_page, paragraph='<p>We have great students</p>')

    # should find a page intro for students
    assert page_intro(rf.get('/people/students/')) == {'page_intro': intro}
    # but not not for staff
    assert page_intro(rf.get('/people/staff/')) == {}
