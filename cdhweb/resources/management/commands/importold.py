import json
import os

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

# Get the user model for use later
User = get_user_model()

# Helper functions for reading the JSON
def load_db(path):
    '''Loads a JSON file and returns the parsed JSON'''
    path = os.path.expanduser(path)
    path = os.path.abspath(path)
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
    missing_args_message = 'Too few arguments: Usage: ./manage.py importold /path/to/cdh1.0/dump.json'
    help = 'Parses a JSON dump from CDH Web 1.0 and imports the data. One time usage intended.'


    def add_arguments(self, parser):
        parser.add_argument('json_file', nargs='+', type=str)

    def handle(self, *args, **options):
        '''Return a list of user emails to test'''
        # TODO: Make this actually import things.
        listing = parse_model('staffprofiles.staffer', load_db(options['json_file'][0]))
        self.stdout.write('Parsing staff profile emails and usernames')
        self.stdout.write('-----')
        for person in listing:
            email = person['fields']['email']
            try:
                self.stdout.write(self.style.SUCCESS(email))
            except AttributeError:
                self.stdout.write(self.style.NOTICE("No email found."))
