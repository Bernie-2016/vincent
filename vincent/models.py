from django.contrib.gis.db import models
from django.contrib.auth.models import User
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
            ('ballots', 'Ballots'),
            ('check-in', 'Check-In'),
            ('machines', 'Machines'),
            ('registration', 'Registration'),
            ('site', 'Site'),
            ('challenge-intimigation', 'Challenge / Intimidation'),
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
    nature = models.CharField(max_length=32, choices=NATURE_CHOICES)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    assignee = models.ForeignKey(User, blank=True, null=True, related_name='assigned_incidents')

    class Meta:
        verbose_name = 'Incident Report'

    def __unicode__(self):
        return '#%s at %s' % (self.pk, self.polling_location)

