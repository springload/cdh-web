from unittest.mock import patch, PropertyMock
from cdhweb.pages.models import (DisplayUrlMixin, ExternalAttachment,
                                 LocalAttachment, RelatedLinkType)


class TestRelatedLinkType:
    def test_str(self):
        restype = RelatedLinkType(name='twitter')
        assert str(restype) == restype.name


class TestLocalAttachment:

    @patch.object(LocalAttachment, "file_extension", new_callable=PropertyMock, return_value="docx")
    def test_str(self, file_ext, db):
        """Local attachment should identify title, author, and file extension"""
        attachment = LocalAttachment(title="My Attachment")
        attachment.title = "My Attachment"
        # no author
        assert str(attachment) == "My Attachment (docx)"
        # with author
        attachment.author = "John Smith"
        assert str(attachment) == "My Attachment, John Smith (docx)"


class TestExternalAttachment:

    def test_str(self, db):
        """External attachment should identify title, author, and display url"""
        attachment = ExternalAttachment(title="My External Attachment",
                                        url="https://google.com?q=foobar")
        # no author
        assert str(attachment) == "My External Attachment (google.com)"
        # with author
        attachment.author = "John Smith"
        assert str(attachment) == \
            "My External Attachment, John Smith (google.com)"


class TestDisplayUrlMixin:

    def test_display_url(self, db):
        """Display URL should remove scheme, params, query, fragment, slashes"""
        class MyDisplayUrlModel(DisplayUrlMixin):
            pass
        model = MyDisplayUrlModel(url="https://google.com/")
        assert model.display_url == "google.com"
        model.url = "http://google.com/foo/bar/baz/"
        assert model.display_url == "google.com/foo/bar/baz"
        model.url = "http://google.com?query=foo"
        assert model.display_url == "google.com"
        model.url = "http://google.com/myplace#subplace"
        assert model.display_url == "google.com/myplace"

