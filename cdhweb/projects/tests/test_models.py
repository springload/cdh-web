from datetime import datetime, timedelta

from cdhweb.pages.models import RelatedLinkType
from cdhweb.projects.models import (
    GrantType,
    Project,
    ProjectField,
    ProjectMethod,
    ProjectRelatedLink,
    ProjectRole,
    Role,
)


class TestGrantType:
    def test_str(self):
        grtype = GrantType(grant_type="Sponsored Project")
        assert str(grtype) == grtype.grant_type


class TestRole:
    def test_str(self):
        role = Role(title="Principal Investigator")
        assert str(role) == role.title


class TestProjectQuerySet:
    def test_current(self, derrida):
        """should query projects with current grant"""
        # derrida latest grant ends today; should be current
        assert Project.objects.current().exists()
        grant = derrida.latest_grant()

        # future end date should also be current
        grant.end_date = datetime.today() + timedelta(days=50)
        grant.save()
        assert Project.objects.current().exists()

        # no end date should also be current
        grant.end_date = None
        grant.save()
        assert Project.objects.current().exists()

        # past end date should not be current
        grant.end_date = datetime.today() - timedelta(days=50)
        grant.save()
        assert not Project.objects.current().exists()

    def test_not_current(self, derrida):
        """should query projects with no current grant"""
        # derrida latest grant ends today; should not be not current
        assert not Project.objects.not_current().exists()
        grant = derrida.latest_grant()

        # future end date should also be current
        grant.end_date = datetime.today() + timedelta(days=50)
        grant.save()
        assert not Project.objects.not_current().exists()

        # no end date should also be current
        grant.end_date = None
        grant.save()
        assert not Project.objects.not_current().exists()

        # past end date should not be current
        grant.end_date = datetime.today() - timedelta(days=50)
        grant.save()
        assert Project.objects.not_current().exists()

    def test_staff_or_postdoc(self, derrida, pliny, ocampo, slavic):
        """should query staff or postdoc projects"""
        staff_postdoc_projects = Project.objects.staff_or_postdoc()
        assert pliny in staff_postdoc_projects  # staff r&d
        assert ocampo in staff_postdoc_projects  # postdoc
        assert derrida not in staff_postdoc_projects  # sponsored
        assert slavic not in staff_postdoc_projects  # working group

    def test_not_staff_or_postdoc(self, derrida, pliny, ocampo, slavic):
        """should query non-staff or postdoc projects"""
        non_staff_postdoc_projects = Project.objects.not_staff_or_postdoc()
        assert derrida in non_staff_postdoc_projects  # sponsored
        assert slavic not in non_staff_postdoc_projects  # working group
        assert pliny not in non_staff_postdoc_projects  # staff r&d
        assert ocampo not in non_staff_postdoc_projects  # postdoc

    def test_not_staff_or_postdoc(self, derrida, pliny, ocampo, slavic):
        """should query working groups"""
        working_groups = Project.objects.working_groups()
        assert slavic in working_groups  # working group
        assert derrida not in working_groups  # sponsored
        assert pliny not in working_groups  # staff r&d
        assert ocampo not in working_groups  # postdoc

    def test_order_by_newest_grant(self, derrida, pliny, ocampo, slavic):
        """should order projects by latest grant"""
        ordered = Project.objects.order_by_newest_grant()
        assert ordered[0] == derrida  # RPG started 1yr ago
        assert ordered[1] == pliny  # started 400 days ago
        assert ordered[2] == ocampo  # started 450 days ago
        assert ordered[3] == slavic  # seed grant 2yrs ago


class TestGrant:
    def test_str(self, derrida, pliny):
        """should display grant type, project title, and start/end dates"""
        # check derrida's margins RPG with both dates
        rpg = derrida.latest_grant()
        assert str(rpg) == "Derrida's Margins: Research Partnership (%s–%s)" % (
            rpg.start_date.year,
            rpg.end_date.year,
        )

        # check pliny r&d grant with no end date
        srg = pliny.latest_grant()
        assert str(srg) == "Pliny Project: Staff R&D (%s–)" % srg.start_date.year


class TestMembership:
    def test_str(self, derrida, pliny):
        # check derrida's margins RPG membership with both dates
        katie = derrida.memberships.get(person__first_name="Katie")
        assert (
            str(katie)
            == "Katie Chenoweth - Project Director on Derrida's Margins (%s)"
            % katie.years
        )
        # check pliny membership with no end date
        ben = pliny.memberships.first()
        assert (
            str(ben) == "Ben Hicks - Project Director on Pliny Project (%s)" % ben.years
        )


class TestProjectRelatedLink:
    def test_display_url(self, derrida):
        """should remove http/https from website url for display"""
        # NOTE tested here because RelatedLink is abstract
        # http
        base_url = "derridas-margins.princeton.edu"
        project_url = "http://%s" % base_url
        website = RelatedLinkType.objects.get_or_create(name="Website")[0]
        res = ProjectRelatedLink.objects.create(
            project=derrida, type=website, url=project_url
        )
        assert res.display_url == base_url

        # https
        res.url = "https://%s" % base_url
        assert res.display_url == base_url


class TestProjectDisplayTags:
    def test_no_values(self, derrida):
        assert derrida.display_tags() == []

    def test_just_role(self, derrida):
        role = ProjectRole(role="test role")
        role.save()
        derrida.role.add(role)
        # should display method and field but not role
        assert derrida.display_tags() == []

    def test_all_relations(self, derrida):
        role1 = ProjectRole(role="test role 1")
        role2 = ProjectRole(role="test role 2")
        method = ProjectMethod(method="test method")
        field = ProjectField(field="test field")
        role1.save()
        role2.save()
        method.save()
        field.save()

        derrida.role.add(role1)
        derrida.role.add(role2)
        derrida.method.add(method)
        derrida.field.add(field)
        assert derrida.display_tags() == [
            "test field",
            "test method",
        ]
