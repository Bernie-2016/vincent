# -*- coding: utf-8 -*-

from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from localflavor.us.models import PhoneNumberField


class County(models.Model):
    gid = models.AutoField(primary_key=True)
    stfips = models.CharField(max_length=2, blank=True, null=True)
    ctfips = models.CharField(max_length=5, blank=True, null=True)
    state = models.CharField(max_length=66, blank=True, null=True)
    county = models.CharField(max_length=66, blank=True, null=True)
    geom = models.MultiPolygonField(srid=4316, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'county'
        verbose_name_plural = 'Counties'


class GeocodedPollingLocation(models.Model):
    precinctid = models.AutoField(primary_key=True, verbose_name='Precinct ID')
    precinctcode = models.CharField(max_length=120, blank=True, null=True, verbose_name='Precinct Code')
    precinctname = models.CharField(max_length=300, blank=True, null=True, verbose_name='Precinct Name')
    addr = models.CharField(max_length=150, blank=True, null=True, verbose_name='Address')
    city = models.CharField(max_length=150, blank=True, null=True)
    state = models.CharField(max_length=6, blank=True, null=True)
    zip = models.CharField(max_length=15, blank=True, null=True)
    pollinglocation = models.CharField(max_length=300, blank=True, null=True, verbose_name='Polling Location')
    pollinglocationdescription = models.CharField(max_length=240, blank=True, null=True, verbose_name='Polling Location Description')
    cass_address = models.TextField(blank=True, null=True)
    cass_address_type = models.CharField(max_length=1, blank=True, null=True)
    cass_carrier_route = models.CharField(max_length=4, blank=True, null=True)
    cass_city = models.CharField(max_length=128, blank=True, null=True)
    cass_dpv = models.CharField(max_length=1, blank=True, null=True)
    cass_dpvfootnotes = models.CharField(max_length=16, blank=True, null=True)
    cass_housenumber = models.CharField(max_length=64, blank=True, null=True)
    cass_postdir = models.CharField(max_length=2, blank=True, null=True)
    cass_predir = models.CharField(max_length=2, blank=True, null=True)
    cass_result_code = models.CharField(max_length=64, blank=True, null=True)
    cass_state = models.CharField(max_length=2, blank=True, null=True)
    cass_streetname = models.CharField(max_length=128, blank=True, null=True)
    cass_streettype = models.CharField(max_length=16, blank=True, null=True)
    cass_timezone = models.CharField(max_length=64, blank=True, null=True)
    cass_unit = models.CharField(max_length=64, blank=True, null=True)
    cass_unittype = models.CharField(max_length=16, blank=True, null=True)
    cass_vacancy = models.CharField(max_length=1, blank=True, null=True)
    cass_zip4 = models.CharField(max_length=4, blank=True, null=True)
    cass_zip5 = models.CharField(max_length=5, blank=True, null=True)
    tsmart_census_id = models.CharField(max_length=64, blank=True, null=True)
    tsmart_geocode_level = models.CharField(max_length=64, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    geocode_failure = models.CharField(max_length=1000, blank=True, null=True)
    geom = models.PointField(blank=True, null=True)

    class Meta:
        managed = False
        verbose_name = 'Polling Location'
        db_table = 'geocoded_polling_locations'

    def __unicode__(self):
        return "%s, %s, %s" % (self.pollinglocation, self.city, self.state)


class IncidentReport(models.Model):
    SCOPE_CHOICES = (
            (1, 'One Voter'),
            (3, 'Some Voters'),
            (5, 'Precinct'),
            (10, 'Polling Place'),
            (20, 'County'),
            (50, 'State'),
        )
    NATURE_CHOICES = (
            ('Ballots', (
                    ('not-enough-ballots', 'Not enough ballots'),
                    ('not-using-paper-ballots-to-compensate-for-machines', 'Not using paper ballots to compensate for machines'),
                    ('wrong-ballots-distributed', 'Wrong ballots distributed'),
                    ('improper-ballot-storage', 'Improper ballot storage'),
                    ('not-enough-provisional-ballots', 'Not enough provisional ballots'),
                    ('improper-use-of-provisional-ballots', 'Improper use of provisional ballots'),
                    ('excessive-use-of-provisional-ballots', 'Excessive use of provisional ballots'),
                    ('failure-to-give-provisional-ballots', 'Failure to give provisional ballots'),
                    ('other-provisional-ballots', 'Other - provisional ballots'),
                    ('other-ballots', 'Other - ballots')
                )
            ),
            ('Check-In', (
                    ('poll-workers-giving-incorrect-voting-instructions', 'Poll workers giving incorrect voting instructions'),
                    ('directing-voters-to-wrong-site-or-failing-to-direct-them-to-correct-one', 'Directing voters to wrong site (or failing to direct them to correct one)'),
                    ('voters-in-line-at-closing-not-allowed-to-vote', 'Voters in line at closing not allowed to vote'),
                    ('slow-check-in-due-to-volume', 'Slow check-in due to volume'),
                    ('language-related-problem', 'Language-related problem'),
                    ('other-check-in-problem', 'Other check-in problem'),
                    ('problem-due-to-absentee-ballot-in-person-vote', 'Problem due to absentee ballot & in-person vote'),
                    ('did-not-receive-absentee-ballot', 'Did not receive absentee ballot'),
                ),
            ),
            ('Machines', (
                    ('machines-not-functional-usable', 'Machines not functional/usable'),
                    ('not-enough-machines', 'Not enough machines'),
                    ('zero-tape-problems', 'Zero tape problems'),
                    ('wrong-vote-result', 'Wrong vote result'),
                    ('other-tally-problems', 'Other tally problems'),
                    ('machine-security-problems', 'Machine security problems'),
                    ('other-machines', 'Other - machines'),
                )
            ),
            ('Registration', (
                    ('registered-but-not-on-the-rolls', 'Registered but not on the rolls'),
                    ('problem-due-to-change-of-address', 'Problem due to change of address'),
                    ('problem-due-to-alleged-criminal-conviction', 'Problem due to alleged criminal conviction'),
                    ('challenge-to-voter-eligibility', 'Challenge to voter eligibility'),
                    ('legitimate-id-not-accepted', 'Legitimate ID not accepted'),
                    ('id-demanded-when-not-necessary', 'ID demanded when not necessary'),
                    ('same-day-registration-delays', 'Same-day registration delays'),
                    ('other-registration-problems', 'Other registration problems'),
                )
            ),
            ('Site', (
                    ('location-closed', 'Location closed'),
                    ('location-not-accessible-to-persons-with-disabilities', 'Location not accessible to persons with disabilities'),
                    ('location-obstructed-or-blocked-off', 'Location obstructed or blocked off'),
                    ('lack-of-parking', 'Lack of parking'),
                    ('signage-problems', 'Signage problems'),
                    ('electioneering', 'Electioneering'),
                    ('not-enough-supplies-or-forms', 'Not enough supplies or forms'),
                    ('other-site-problems', 'Other - site problems'),
                    ('site-problems-due-to-not-enough-officials', 'Site problems due to not enough officials'),
                    ('site-problems-due-to-not-enough-voting-booths', 'Site problems due to not enough voting booths'),
                    ('inefficient-poll-workers', 'Inefficient poll workers'),
                    ('slow-check-in-system', 'Slow check-in system'),
                    ('undue-restrictions-on-observer', 'Undue restrictions on observer'),
                )
            ),
            ('Challenge / Intimidation', (
                    ('misinformation', 'Misinformation'),
                    ('citizenship-based-challenges', 'Citizenship-based challenges'),
                    ('residence-based-challenges', 'Residence-based challenges'),
                    ('id-based-challenges', 'ID-based challenges'),
                    ('other-challenges', 'Other challenges'),
                    ('unhelpful-law-enforcement-presence', 'Unhelpful law enforcement presence'),
                    ('poll-worker-interference', 'Poll worker interference'),
                    ('other-harassment', 'Other harassment'),
                )
            ),
            ('id-issues', 'ID Issues'),
            ('17-yo-voting', '17 Year Old Voting'),
        )
    STATUS_CHOICES = (
            ('new', 'New'),
            ('assigned', 'Assigned'),
            ('resolved', 'Resolved'),
            ('closed', 'Closed')
        )
    creator = models.ForeignKey(User, blank=True, null=True, related_name='incidents_created')
    creator_name = models.CharField(max_length=128)
    creator_email = models.EmailField(max_length=128)
    creator_phone = models.CharField(max_length=128) # localize
    reporter_name = models.CharField(max_length=128)
    reporter_phone = PhoneNumberField(max_length=128)
    # county = models.ForeignKey(County)
    polling_location = models.ForeignKey(GeocodedPollingLocation, db_constraint=False)
    time = models.DateTimeField(auto_now_add=True)
    scope = models.IntegerField(choices=SCOPE_CHOICES)
    nature = models.CharField(max_length=128, choices=NATURE_CHOICES)
    long_line = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    assignee = models.ForeignKey(User, blank=True, null=True, related_name='assigned_incidents')

    class Meta:
        verbose_name = 'Incident Report'

    def __unicode__(self):
        return '#%s - %s' % (self.pk, self.get_nature_display())

    def get_absolute_url(self):
        return reverse('incident_detail', kwargs={'pk': self.pk})


class Comment(models.Model):
    incident_report = models.ForeignKey(IncidentReport)
    author = models.ForeignKey(User)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']


class PhoneNumber(models.Model):
    user = models.ForeignKey(User)
    phone_number = PhoneNumberField(max_length=128)


class AssignedLocation(models.Model):
    user = models.OneToOneField(User)
    polling_location = models.ForeignKey(GeocodedPollingLocation, db_constraint=False)
    fulfilled = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)