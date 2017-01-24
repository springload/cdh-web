import datetime
import json
import os

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from cdhweb.people.models import Title, Position

# Get the user model for use later
User = get_user_model()

# Helper functions for reading the JSON
def load_db(path):
    '''Loads a JSON file and returns the parsed JSON'''
    with open(path, 'r') as fp:
        return json.load(fp)

def parse_model(model_name, json_stream):
    '''Takes the name of a django model, json stream, and returns a list'''
    new_list = []

    for data in json_stream:
        if data['model'] == model_name:
            new_list.append(data)
    return new_list


class Command(BaseCommand):
    missing_args_message = ('Too few arguments: Usage: ./manage.py importold'
                            '/path/to/cdh1.0/dump.json')
    help = ('Parses a JSON dump from CDH Web 1.0 and'
            'imports the data. One time usage intended.')

    def add_arguments(self, parser):
        parser.add_argument('json_file',
            help='Path to a JSON dump created using dumpdata',
            type=str
        )
        parser.add_argument(
            '--noop',
            action='store_true',
            help="Don't write to database, only log process"
        )

    def handle(self, *args, **options):
        '''Return a list of user emails to test'''
        # TODO: Make this actually import (all the) things.
        # TODO: Clean up line breaks as sensible
        # Parse the database
        try:
            db = load_db(options['json_file'])
        except:
            self.stdout.write(self.style.ERROR("Couldn't open JSON file."))

        # Parse staff profiles
        listing = parse_model('staffprofiles.staffer', db)
        staff_pages = parse_model('staffprofiles.stafferpage', db)
        if options['noop']:
            self.stdout.write(self.style.NOTICE('Running in no-op mode'))
        self.stdout.write('Importing staff profiles with matches on new site')
        self.stdout.write('-----')

        # Iterate over people and add their listings
        for person in listing:
            result_dict = {}
            email = person['fields']['email']
            try:
                user = User.objects.get(email=email)
                self.stdout.write(self.style.SUCCESS('Found username %s')
                                  % user.username)
                # Education
                user.profile.education = person['fields']['education']
                self.stdout.write('Education: %s' % user.profile.education)
                result_dict['education'] = True
                # Bio
                for page in staff_pages:
                    name = person['fields']['name']
                    slugged_name = name.lower().strip().replace(" ", "-")
                    if page['fields']['slug'] == slugged_name:
                        user.profile.bio = page['fields']['extra_content']
                        self.stdout.write('Bio: %s...' %
                                          str(user.profile.bio)[:30])
                        result_dict['bio'] = True
                # Title
                title_data = person['fields']['title']
                # TODO: Create a sort order import -- need to know how sort
                # will be used
                self.stdout.write('Title: %s' % title_data)
                if not options['noop']:
                    title_obj, created =\
                        Title.objects.get_or_create(title=title_data)
                    if created:
                        title_obj.save()
                    result_dict['title'] = True
                # Save if not noop
                if not options['noop']:
                    user.profile.save()
                    position, created = Position.objects.get_or_create(
                            user=user,
                            title=title_obj,
                            start_date=datetime.date(2016, 8, 1)
                            )
                    position.save()
                    result_dict['position'] = True
                    for k, v in result_dict.items():
                        self.stdout.write(self.style.SUCCESS('Wrote %s for %s'
                                          % (k, user.username)))
            except:
                self.stdout.write(self.style.NOTICE("No matching user for %s"
                                                    % person['fields']['name']))
