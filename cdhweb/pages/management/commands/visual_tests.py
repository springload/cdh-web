from django.core.management import call_command
from django.core.management.base import BaseCommand
from percy import percy_snapshot
from selenium import webdriver


class Command(BaseCommand):
    """Execute visual regression tests against a running django server."""

    help = __doc__

    def get_browser(self):
        """Initialize a browser driver to use for taking snapshots."""
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--headless")
        return webdriver.Chrome(options=options)

    def take_snapshots(self, browser):
        """Take DOM snapshots of a set of URLs and upload to Percy."""

        # homepage
        browser.get("http://localhost:8000/")
        browser.find_element_by_css_selector("label.open").click()
        browser.find_element_by_css_selector("input[type=search]").send_keys("digital")
        percy_snapshot(browser, "Home")

        # landing page
        browser.get("http://localhost:8000/landing")
        percy_snapshot(browser, "Landing Page")

        # content page
        browser.get("http://localhost:8000/landing/content")
        percy_snapshot(browser, "Content Page")

        # projects list page
        browser.get("http://localhost:8000/projects/sponsored")
        browser.find_element_by_class_name("toggle").click()  # expand dropdown
        percy_snapshot(browser, "Projects List Page")

        # project page
        browser.get("http://localhost:8000/projects/derridas-margins/")
        percy_snapshot(browser, "Project Page")

        # people list page
        browser.get("http://localhost:8000/people/staff")
        browser.find_element_by_class_name("toggle").click()
        percy_snapshot(browser, "Person List Page")

        # profile page
        browser.get("http://localhost:8000/people/staffer/")
        percy_snapshot(browser, "Profile Page")

        # events list page
        browser.get("http://localhost:8000/events")
        browser.find_element_by_class_name("toggle").click()
        percy_snapshot(browser, "Events List Page")

        # event page
        browser.get("http://localhost:8000/events/2017/02/testing-course/")
        percy_snapshot(browser, "Event Page")

        # blog list page
        browser.get("http://localhost:8000/updates")
        browser.find_element_by_class_name("toggle").click()
        percy_snapshot(browser, "Blog List Page")

        # blog post
        browser.get("http://localhost:8000/updates/2021/07/06/a-big-announcement/")
        percy_snapshot(browser, "Blog Post")

        # 404 page
        browser.get("http://localhost:8000/bad-url")
        percy_snapshot(browser, "404 Page")

        # 500 page
        browser.get("http://localhost:8000/500")
        percy_snapshot(browser, "500 Page")

        # site search
        browser.get("http://localhost:8000/search?q=digital")
        percy_snapshot(browser, "Site Search")

    def handle(self, *args, **options):
        # index pages in wagtail search backend
        call_command("update_index")

        # spin up browser and take snapshots; shut down when finished
        browser = self.get_browser()
        self.take_snapshots(browser)
        browser.quit()
