from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from django.core.urlresolvers import reverse
from django.template.defaultfilters import truncatewords
from django.utils.html import format_html
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


@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    actions = None  # this will need changing.
    fields = ['nature', 'long_line', 'scope', 'polling_location', 'reporter_name', 'reporter_phone', 'reporter_role', 'assignee', 'status', 'creator_name', 'creator_email', 'creator_phone', 'description']
    inlines = [CommentInline]
    list_display = ['summary', 'assignee', 'status']
    list_display_links = ['summary']
    list_filter = ['polling_location__state', IncidentReportCountyFilter, 'long_line', 'assignee', 'status']
    list_select_related = ['polling_location', 'assignee']
    raw_id_fields = ['polling_location']
    search_fields = ['nature', 'description', 'polling_location__precinctcode', 'polling_location__addr', 'polling_location__city', 'polling_location__state', 'polling_location__zip']

    def summary(self, obj):
        return format_html('<h3><a href="{}">#{} &mdash; {} &mdash; {}</a></h3><p><strong>{}</strong></p><p style="font-weight: normal;">{}</p>',
                        reverse('admin:vincent_incidentreport_change', args=[obj.pk]),
                        obj.pk,
                        obj.get_nature_display(),
                        obj.created.strftime("%-I:%M:%S %p, %b %-d"),
                        obj.polling_location,
                        truncatewords(obj.description, 60))


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