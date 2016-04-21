from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
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
        return County.objects.filter(state__in=states_spelled_out).defer('geom').values_list('gid', 'county')

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(geom__within=County.objects.get(pk=self.value()).geom)
        return queryset


@admin.register(County)
class CountyAdmin(OSMGeoAdmin):
    list_display = ['county', 'state']
    list_filter = ['state']
    search_fields = ['county']


@admin.register(GeocodedPollingLocation)
class GeocodedPollingLocationAdmin(OSMGeoAdmin):
    actions = None
    list_display = ['pollinglocation', 'addr', 'city', 'state', 'zip']
    list_filter = ['state', CountyFilter]
    search_fields = ['pollinglocation', 'precinctcode', 'addr', 'city', 'state', 'zip']


@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    actions = None  # this will need changing.
    list_display = ['__unicode__', 'scope', 'nature', 'reporter_name', 'assignee', 'status']
    list_filter = ['polling_location__state']
    raw_id_fields = ['polling_location']
