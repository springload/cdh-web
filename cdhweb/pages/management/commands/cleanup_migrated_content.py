import re

from django.core.management.base import BaseCommand
from wagtail.core.models import Page


class Command(BaseCommand):

    # list of regex patterns to replace with a single space
    re_to_space = [
        # non-breaking space
        re.compile(r"&nbsp;"),
        # two or more whitespaces
        re.compile(r"\s\s+"),
    ]

    # list of regex patterns to replace with first match
    re_replace_g1 = [
        # spans with no attributes
        re.compile(r"<span>(((?!</span>).)*)</span>", flags=re.DOTALL),
        # remove all but one space before open inline tag
        re.compile(r"[\n ]+( <(a|em|b|strong|i|span))"),
        # remove white space after end of open inline tag
        re.compile(r"(<(a|em|b|strong|i|span)[^>]*>)[\n ]+"),
        # remove white space before end inline tag
        re.compile(r"[\n ]+(</(a|em|b|strong|i|span)[^>]*>)"),
        # remove newline or whitespace between inline tag end and punctuation
        re.compile(r"(</(a|em|b|strong|i|span)>)[\n ]+(?=[.,;])"),
        # newline + whitespace after opening <p> or <div>
        re.compile(r"(<p>|<div>)[\n ]+"),
    ]

    # list of regex patterns to remove
    re_remove = [
        # opening html & body tags
        re.compile(r"^<html>\s*<body>\s"),
        # closing html & body tags
        re.compile(r"\s*</body>\s*</html>$"),
        # empty div
        re.compile(r"[\n ]+<div>\s*</div>"),
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--noact",
            action="store_true",
            default=False,
            help="Don't save any changes to the database",
        )

    def handle(self, *args, **options):
        v_normal = 1
        verbosity = options["verbosity"]
        noact = options["noact"]
        inline_styles = []
        for page in Page.objects.all():
            realpage = page.get_specific()
            # skip pages with no body content
            if not hasattr(realpage, "body"):
                continue
            for block in realpage.body:
                # assuming only one migrated block per page
                if block.block_type == "migrated":
                    html = block.value.source
                    cleaned_html = self.clean_html(html)
                    block.value.source = cleaned_html
                    if verbosity > v_normal:
                        self.stdout.write(
                            "\n\nHTML before cleanup for %s\n*****\n%s\n*****"
                            % (page.get_full_url(), html)
                        )
                        self.stdout.write(
                            "HTML after cleanup:\n%s\n*****" % cleaned_html
                        )

                    # unless noact mode has been requested, save new revision
                    if not noact:
                        new_revision = realpage.save_revision()
                        # publish new revision if the page is live
                        if realpage.live:
                            new_revision.publish()

                    if 'style="' in cleaned_html:
                        inline_styles.append(realpage.get_full_url())

        if inline_styles:
            print("\nPages with inline styles:\n")
            print("\n".join(inline_styles))

    def clean_html(self, html):
        # remove these regexes
        for regex in self.re_remove:
            html = regex.sub("", html)

        # replace these regexes with first match
        for regex in self.re_replace_g1:
            html = regex.sub(r"\1", html)

        # replace these regexes with single space
        for regex in self.re_to_space:
            html = regex.sub(" ", html)

        return html
