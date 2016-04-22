from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from .views import index, IncidentList, IncidentDetail

urlpatterns = [
    url(r'^$', index),
    url(r'^incidents$', login_required(IncidentList.as_view()), name='incident_list'),
    url(r'^incidents/(?P<pk>\d+)', login_required(IncidentDetail.as_view()), name='incident_detail'),
    url(r'^admin/', admin.site.urls),
]

admin.site.site_header = 'Vincent Administration'