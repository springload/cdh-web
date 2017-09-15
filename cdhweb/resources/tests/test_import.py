from io import StringIO
import json
import os
from unittest.mock import Mock, patch

import dateutil.parser
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from pucas.ldap import LDAPSearchException
import pytest

from cdhweb.people.models import Person, Title, Position
from cdhweb.resources.management.commands import import_datav1


FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
    '..', 'fixtures')


class TestImportCommand(TestCase):

    test_data = os.path.join(FIXTURE_DIR, 'test_import_data.json')

    def setUp(self):
        self.cmd = import_datav1.Command()
        self.cmd.stdout = StringIO()
        self.cmd.stderr = StringIO()
        self.cmd.current_site = Site.objects.get_current()

    def test_run(self):
        # nonexistent file path
        bad_file_path = '/tmp/not/a/real/file'
        with pytest.raises(CommandError) as err:
            call_command(self.cmd, bad_file_path)
        assert "No such file or directory: '%s'" % bad_file_path in \
            str(err)

        # non-json file path
        bad_file_path = __file__
        with pytest.raises(CommandError) as err:
            call_command(self.cmd, bad_file_path)
        assert "Error parsing JSON" in str(err)

        # modes
        with patch.object(self.cmd, 'import_profiles') as mock_import_profile:
            with patch.object(self.cmd, 'import_events') as mock_import_events:
                # import people only
                call_command(self.cmd, '--people', self.test_data)
                mock_import_events.assert_not_called()
                assert mock_import_profile.call_args
                mock_import_profile.reset_mock()

                # import events only
                call_command(self.cmd, '--events', self.test_data)
                mock_import_profile.assert_not_called()
                assert mock_import_events.call_args
                mock_import_events.reset_mock()

                # no arg, run all imports
                call_command(self.cmd, self.test_data)
                assert mock_import_profile.call_args
                assert mock_import_events.call_args


    @patch('cdhweb.resources.management.commands.import_datav1.user_info_from_ldap')
    def test_init_user(self, mockuserfromldap):
        test_netid = 'foo'
        email = '%s@example.com' % test_netid
        staffdata = Mock()
        self.cmd.init_user(email, staffdata)
        # user should exist
        user = Person.objects.get(username=test_netid)
        assert user
        # ldap init should have been called
        mockuserfromldap.assert_called_with(user)

        # re-init does not recreate
        self.cmd.init_user(email, staffdata)
        assert Person.objects.filter(username=test_netid).count() == 1

        # email alias
        test_netid = 'rebecca.s.koeser'
        email = '%s@example.com' % test_netid
        self.cmd.init_user(email, staffdata)
        # alias should be used rather than email name
        assert Person.objects.get(username=self.cmd.email_aliases[test_netid])

        # simulate ldap exception and set data from import
        mockuserfromldap.side_effect = LDAPSearchException
        test_netid = 'foo'
        email = '%s@example.com' % test_netid
        staffdata.fields.email = email
        first, last = 'Joe G.', 'Smith'
        staffdata.fields.name = ' '.join([first, last])
        self.cmd.init_user(email, staffdata)
        user = Person.objects.get(username=test_netid)
        assert user.email == email
        assert user.first_name == first
        assert user.last_name == last
        assert user.profile
        assert user.profile.title == staffdata.fields.name

    def test_import_profiles(self):
        with open(self.test_data) as datafile:
            data = json.load(datafile)

        # create test user
        # user = Person.objects.create(username='claus',
            # email=data[0]['fields']['email'])
        def mock_init_user(*args, **kwargs):
            return Person.objects.create(username='claus')

        stafferdata = data[0]['fields']
        pagedata = data[1]['fields']

        with patch.object(self.cmd, 'init_user', new=mock_init_user):
            # mock_init_user.return_value = user
            self.cmd.import_profiles(data)
            # mock_init_user.assert_called_with(data[0]['fields']['email'],
                # AttrDict(data[0]))

        # get updated record and check
        user = Person.objects.get(username='claus')
        assert user.profile
        assert stafferdata['education'] in user.profile.education
        assert user.profile.is_staff
        assert user.profile.site == self.cmd.current_site
        jobtitle = Title.objects.get(title=stafferdata['title'])
        assert jobtitle
        assert Position.objects.get(title=jobtitle, user=user)
        # displayable page data
        assert user.profile.bio == pagedata['extra_content']
        assert user.profile.slug == pagedata['slug']
        assert user.profile.status == pagedata['status']

        assert user.profile.description == pagedata['description']
        assert user.profile.gen_description == pagedata['gen_description']
        assert user.profile.publish_date == \
            dateutil.parser.parse(pagedata['publish_date'])
        assert user.profile.created == \
            dateutil.parser.parse(pagedata['created'])

