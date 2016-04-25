import csv
import random
import warnings

from django.contrib.auth.models import User, Group
from django.core.mail.message import EmailMultiAlternatives
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.utils.html import linebreaks, urlize
from localflavor.us.forms import phone_digits_re
from optparse import make_option

from ...models import PhoneNumber


class Command(BaseCommand):
    NEEDED_FIELDS = ['First Name', 'Last Name', 'Email', 'Phone', 'Group']
    STAFF_GROUPS = ['Incident Report Admins']
    help = 'Adds new users.'

    def add_arguments(self, parser):
        parser.add_argument('filename',
            type=str,
            nargs=1,
            help='Filename of CSV to import')
        parser.add_argument('-f',
            action='store_true',
            dest='force',
            default=False,
            help='Run the import. Otherwise, this will be a dry run.')
        parser.add_argument('-e',
            action='store_true',
            dest='send_email_invites',
            default=False,
            help='Email invites to users now.')

    def _reset(self):
        self.file.seek(0)
        self.file.readline()
        return True

    def handle(self, *args, **options):

        filename = options['filename'][0]
        self.file = open(filename, 'r')
        csv_file = csv.DictReader(self.file)

        if csv_file.fieldnames != self.NEEDED_FIELDS:
            raise CommandError("We're expecting these fields: %s" % self.NEEDED_FIELDS)

        # check group names
        all_groups = set(Group.objects.values_list('name', flat=True))
        outstanding_group_names = set(map(lambda p: p['Group'], filter(lambda p: p['Group'] not in all_groups, csv_file)))

        if len(outstanding_group_names) > 0:
            warnings.warn("These groups are not setup yet: %s" % (', '.join(outstanding_group_names)))

        self._reset()

        # check phone numbers
        phone_numbers = map(lambda p: p['Phone'], csv_file)
        invalid_phone_numbers = []
        for phone in phone_numbers:
            if not phone_digits_re.match(phone):
                invalid_phone_numbers.append(phone)

        if invalid_phone_numbers:
            warnings.warn("These phone numbers are not valid: %s" % (', '.join(invalid_phone_numbers)))

        self._reset()

        # check emails
        email_addresses = map(lambda p: p['Email'], csv_file)
        invalid_email_addresses = []
        for email in email_addresses:
            try:
                validate_email(email)
            except:
                invalid_email_addresses.append(email)

        if invalid_email_addresses:
            warnings.warn("These email addresses are not valid: %s" % (', '.join(invalid_email_addresses)))

        self._reset()

        # check if email is already in system?
        existing_email = User.objects.filter(email__in=email_addresses)

        if existing_email.count():
            warnings.warn("These email addresses already have users: %s" % (', '.join(existing_email.values_list('email', flat=True))))

        if not options['force']:
            print "Dry run complete! Run again with '-f' argument to run import."
            exit(0)

        keyify = {
            'First Name': 'first_name',
            'Last Name': 'last_name',
            'Email': 'email'
        }

        group_names_and_ids = dict((group[0], group[1]) for group in Group.objects.values_list('id', 'name'))

        for person in csv_file:
            
            phone_number = person.pop('Phone')
            group_name = person.pop('Group')

            person_kwargs = dict((keyify[k], v) for k,v in person.iteritems())
            person_kwargs['username'] = ''.join([person['First Name'], person['Last Name']]).lower()

            person_kwargs['password'] = "bernievopro%s" % random.randint(20,99)

            if group_name in self.STAFF_GROUPS:
                person_kwargs['is_staff'] = True

            if group_name == 'Superusers':
                person_kwargs['is_superuser'] = True
            
            new_user = User.objects.create(**person_kwargs)

            Group.objects.get(name=group_name).user_set.add(new_user)

            if phone_number:
                PhoneNumber.objects.create(user=new_user, phone_number=phone_number)

            print "Created new user '%s' with email '%s' and password '%s'" % (new_user.username, new_user.email, person_kwargs['password'])

            if options['send_email_invites']:

                email_body_tpl = """Hi %(first_name)s,

You've been invited to use Vincent, a new voter incident tracking system.

Your username is %(username)s. Please use this one-time link to login and set a memorable password:

https://vincent.berniesanders.com/?username=%(username)s&password=%(password)s

After that, you'll be ready to go. Just login here:

https://vincent.berniesanders.com/

Feel free to respond to this email if you have any troubles and we'll get you sorted.

Thank you!

Jon"""

                plain_text_body = email_body_tpl % {'first_name': new_user.first_name,
                                                    'username': new_user.username,
                                                    'password': person_kwargs['password']}

                html_body = linebreaks(urlize(plain_text_body))


                email_message = EmailMultiAlternatives(subject='Welcome to Vincent, a new voter incident tracking system',
                                body=plain_text_body,
                                from_email='Jon Culver <jonculver@berniesanders.com>',
                                to=[new_user.email],
                                headers={'X-Mailgun-Track': False})

                email_message.attach_alternative(html_body, "text/html")

                email_message.send(fail_silently=False)


        print "Users created!"
