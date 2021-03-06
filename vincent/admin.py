from django.contrib import admin
from django.contrib.auth.models import User
from django.core.mail.message import EmailMultiAlternatives
from django.utils.html import linebreaks, urlize
from django.contrib.gis.admin import OSMGeoAdmin
from django.core.urlresolvers import reverse
from django.template.defaultfilters import truncatewords
from django.utils.functional import curry
from django.utils.html import format_html
from django.utils.timezone import template_localtime
from localflavor.us.us_states import US_STATES
from .models import *


class CountyFilter(admin.SimpleListFilter):
    title = 'County'
    parameter_name = 'county'

    def lookups(self, request, model_admin):
        states = request.GET.get('state', None)
        if not states:
            return ()
        states_spelled_out = map(lambda state: unicode(state[1]), filter(lambda state: state[0] in states.split(','), US_STATES))
        return County.objects.filter(state__in=states_spelled_out).defer('geom').order_by('county').values_list('gid', 'county')

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(geom__within=County.objects.get(pk=self.value()).geom)
        return queryset


class IncidentReportCountyFilter(admin.SimpleListFilter):
    title = 'County'
    parameter_name = 'county'

    def lookups(self, request, model_admin):
        states = request.GET.get('polling_location__state', None)
        if not states:
            return ()
        states_spelled_out = map(lambda state: unicode(state[1]), filter(lambda state: state[0] in states.split(','), US_STATES))
        return County.objects.filter(state__in=states_spelled_out).defer('geom').order_by('county').values_list('gid', 'county')

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(polling_location__geom__within=County.objects.get(pk=self.value()).geom)
        return queryset


class AssigneeFilter(admin.SimpleListFilter):
    title = 'Assignee'
    parameter_name = 'assignee'

    def lookups(self, request, model_admin):
        users_with_assignments = User.objects.filter(assigned_incidents__isnull = False).distinct().order_by('first_name')

        def concat_first_last_name(user):
            return (user.id, user.first_name + ' ' + user.last_name)
        return map(concat_first_last_name, users_with_assignments)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(assignee_id=self.value())
        return queryset


class StatusFilter(admin.SimpleListFilter):
    title = 'Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        choices = list(IncidentReport.STATUS_CHOICES)
        choices.insert(0, ('new+assigned', 'New or Assigned'))
        return choices

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        else:
            filters = {'status': value}
            if '+' in value:
                filters = {'status__in': value.split('+')}
            return queryset.filter(**filters)


@admin.register(County)
class CountyAdmin(OSMGeoAdmin):
    list_display = ['county', 'state']
    list_filter = ['state']
    search_fields = ['county']


class IncidentReportInline(admin.StackedInline):
    model = IncidentReport


@admin.register(GeocodedPollingLocation)
class GeocodedPollingLocationAdmin(OSMGeoAdmin):
    actions = None
    inlines = [IncidentReportInline]
    list_display = ['pollinglocation', 'addr', 'city', 'state', 'zip']
    list_filter = ['state', CountyFilter]
    search_fields = ['pollinglocation', 'precinctcode', 'addr', 'city', 'state', 'zip']


class CommentInline(admin.StackedInline):
    model = Comment

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(CommentInline, self).get_formset(request, obj, **kwargs)
        initial = [{
            'author': request.user,
        }]
        formset.__init__ = curry(formset.__init__, initial=initial)
        return formset


@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    actions = None  # this will need changing.
    fields = ['nature', 'long_line', 'scope', 'polling_location', 'reporter_name', 'reporter_phone', 'reporter_role', 'assignee', 'status', 'creator_name', 'creator_email', 'creator_phone', 'description']
    inlines = [CommentInline]
    list_display = ['summary', 'priority', 'assignee', 'status']
    list_display_links = ['summary']
    list_filter = [StatusFilter, 'polling_location__priority', 'polling_location__state', IncidentReportCountyFilter, 'long_line', AssigneeFilter]
    list_select_related = ['polling_location', 'assignee']
    raw_id_fields = ['polling_location']
    search_fields = ['nature', 'description', 'polling_location__precinctcode', 'polling_location__addr', 'polling_location__city', 'polling_location__state', 'polling_location__zip']

    def priority(self, obj):
        return obj.polling_location.priority if obj.polling_location else 4

    def summary(self, obj):
        return format_html('<h3><a href="{}">#{} &mdash; {}: {}</a></h3><p><strong>Created: {} | Location: {}</strong></p><p style="font-weight: normal;">{}</p>',
                        reverse('admin:vincent_incidentreport_change', args=[obj.pk]),
                        obj.pk,
                        obj.get_scope_display(),
                        obj.get_nature_display(),
                        template_localtime(obj.created).strftime("%-I:%M:%S %p, %b %-d"),
                        obj.polling_location,
                        truncatewords(obj.description, 60))

    def save_model(self, request, obj, form, change):
        obj.save()

        #Send email for newly assigned incidents
        if ('assignee' in form.changed_data or change == False) and obj.assignee != None:
            email_body_tpl = """Hi %(first_name)s,

You have been assigned a new incident. To follow up, click this link:
https://vincent.berniesanders.com/incidents/%(incident_id)s

Reported by:
%(reporter_name)s
%(reporter_phone)s

Type: %(type)s

Description:
%(description)s"""

            plain_text_body = email_body_tpl % {'first_name': obj.assignee.first_name,
                                                'description': obj.description,
                                                'type': obj.nature,
                                                'reporter_name': obj.reporter_name,
                                                'reporter_phone': obj.reporter_phone,
                                                'incident_id': obj.id}

            html_body = linebreaks(urlize(plain_text_body))


            email_message = EmailMultiAlternatives(subject='New Vincent Assignment',
                            body=plain_text_body,
                            from_email='Voter Incident Reporting System <voterprotection@berniesanders.com>',
                            to=[obj.assignee.email],
                            reply_to=[obj.creator_email, 'reneeparadis@berniesanders.com'],
                            headers={'X-Mailgun-Track': False})

            email_message.attach_alternative(html_body, "text/html")

            email_message.send(fail_silently=False)


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    actions = None
    list_display = ['user', 'phone_number']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone_number']


@admin.register(AssignedLocation)
class AssignedLocationAdmin(admin.ModelAdmin):
    actions = None
    list_display = ['user', 'polling_location', 'fulfilled']
    raw_id_fields = ['polling_location']

    def save_model(self, request, obj, form, change):
        obj.save()
        
        #Send email for newly assigned locations
        if 'user' in form.changed_data or 'polling_location' in form.changed_data:
            email_body_tpl = """Hi %(first_name)s,

We need you to relocate to a new polling location. Click here to get directions and check in once you're there:
https://vincent.berniesanders.com/assigned-location

Polling Location:
%(pollinglocation)s
%(addr)s
%(cass_city)s %(cass_state)s, %(cass_zip5)s
"""

            plain_text_body = email_body_tpl % {'first_name': obj._user_cache.first_name,
                                                'pollinglocation': obj._polling_location_cache.pollinglocation,
                                                'addr': obj._polling_location_cache.addr,
                                                'cass_city': obj._polling_location_cache.cass_city,
                                                'cass_state': obj._polling_location_cache.cass_state,
                                                'cass_zip5': obj._polling_location_cache.cass_zip5}

            html_body = linebreaks(urlize(plain_text_body))


            email_message = EmailMultiAlternatives(subject='New Voter Protection Location Assignment',
                            body=plain_text_body,
                            from_email='Voter Incident Reporting System <voterprotection@berniesanders.com>',
                            to=[obj._user_cache.email],
                            reply_to=['reneeparadis@berniesanders.com'],
                            headers={'X-Mailgun-Track': False})

            email_message.attach_alternative(html_body, "text/html")

            email_message.send(fail_silently=False)
