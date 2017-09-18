from django.test import TestCase

from cdhweb.resources.models import Attachment, ResourceType

class TestAttachment(TestCase):

    def test_str(self):
        attach = Attachment(title='My Document')
        assert str(attach) == attach.title


class TestResourceType(TestCase):

    def test_str(self):
        restype = ResourceType(name='twitter')