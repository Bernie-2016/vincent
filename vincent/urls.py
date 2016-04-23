from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from .views import index, AssignedLocation, CommentCreate, \
        IncidentList, IncidentDetail, IncidentCreate, PollingPlace

urlpatterns = [
    url(r'^$', index),
    url(r'^incidents$', login_required(IncidentList.as_view()), name='incident_list'),
    url(r'^incidents/add$', login_required(IncidentCreate.as_view()), name='incident_add'),
    url(r'^incidents/(?P<pk>\d+)$', login_required(IncidentDetail.as_view()), name='incident_detail'),
    url(r'^incidents/(?P<pk>\d+)/add-comment$', login_required(CommentCreate.as_view()), name='comment_create'),
    url(r'^assigned-location$', login_required(AssignedLocation.as_view()), name='assigned_location'),
    url(r'^polling-places/lookup$', PollingPlace.as_view(), name='lookup'),
    url(r'^admin/', admin.site.urls),
]

admin.site.site_header = 'Vincent Administration'