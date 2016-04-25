from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import CreateView, DetailView, ListView, View
from django.views.generic.base import ContextMixin


from .forms import CommentForm, IncidentReportForm
from .models import AssignedLocation, Comment, GeocodedPollingLocation, IncidentReport

def index(request):

    # are they logged in already? on to the incidents.
    if request.method == 'GET' and request.user.is_authenticated() and request.user.is_active:
        return redirect('/incidents')


    login_form = AuthenticationForm(data=request.POST or None)
    if request.method == 'POST':
        if login_form.is_valid():
            username, password = login_form.cleaned_data['username'], login_form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                login(request, user)
                return redirect('/incidents')
            else:
                login_form.add_error(None, "Your user is inactive.")

    # note -- may be returned in both GET and POST requests
    # (POST if their user/pass is invalid or inactive)
    return render(request, 'login.html', {'login_form': login_form})


class IncidentList(ListView):
    
    def get_queryset(self):
        return IncidentReport.objects.filter(assignee=self.request.user, status__in=['new', 'assigned']).select_related('polling_location')


class CommentCreate(CreateView):
    model = Comment
    form_class = CommentForm

    def get_initial(self):
        return {'author': self.request.user}

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, 'Your comment has been added.')
        return self.object.incident_report.get_absolute_url()


class IncidentDetail(DetailView):
    model = IncidentReport

    def get_context_data(self, **kwargs):
        context = super(IncidentDetail, self).get_context_data(**kwargs)
        context['comment_form'] = CommentForm(initial={'author': self.request.user, 'incident_report': self.object})
        return context


class IncidentCreate(CreateView):
    form_class = IncidentReportForm
    model = IncidentReport

    def get_initial(self):
        initial = {'creator_name': self.request.user.get_full_name(),
                'creator_email': self.request.user.email,
                'creator': self.request.user }
        try:
            initial['creator_phone'] = self.request.user.phonenumber_set.first().phone_number
        except:
            pass
        return initial


    def get_success_url(self):
        url_and_title = {'url': self.object.get_absolute_url(),
                            'title': unicode(self.object) }
        messages.add_message(self.request, messages.SUCCESS, 'Your new incident report <a href="%(url)s">%(title)s</a> has been created. Add another below.' % url_and_title)
        return reverse('incident_add')


class PollingPlace(View):
    DISTANCE_IN_MILES = 5

    def text_search(self, request, *args, **kwargs):
        filters = Q()
        for field in ['pollinglocation', 'addr', 'city', 'state', 'zip']:
            filters = filters | Q(**{'%s__icontains' % field: self.q})
        return self.get_json_response_from_filters(filters=filters, search_type='text', ordering=['pollinglocation'])

    def geo_lookup(self, request, *args, **kwargs):
        point = Point(x=float(self.lng), y=float(self.lat), srid=4326)
        return self.get_json_response_from_filters(filters=Q(geom__distance_lte=(point, D(mi=self.DISTANCE_IN_MILES))), search_type='geo', annotations={'distance': Distance('geom', point)}, ordering=['distance'])

    def get_json_response_from_filters(self, filters, search_type='geo', annotations={}, ordering=[]):
        queryset = GeocodedPollingLocation.objects.filter(filters).annotate(**annotations).order_by(*ordering)
        keys = ['precinctid', 'pollinglocation', 'precinctname', 'addr', 'city', 'state', 'zip']
        polling_locations = [loc for loc in queryset.values(*keys)]
        return JsonResponse(data={'results': polling_locations, 'search_type': search_type}, safe=False)

    def get(self, request, *args, **kwargs):
        self.q = request.GET.get('q', None)
        self.lat = request.GET.get('lat', None)
        self.lng = request.GET.get('lng', None)

        if self.q:
            return self.text_search(request, *args, **kwargs)

        elif (self.lat and self.lng):
            return self.geo_lookup(request, *args, **kwargs)
        
        return JsonResponse(data={'error': 'Missing either `q` search parameter, or `lat` and `lng`.'})


class AssignedLocation(DetailView):

    def get_object(self):
        return self.request.user.assignedlocation

    def post(self, request, *args, **kwargs):
        location = self.get_object()
        location.fulfilled = True
        location.save()
        messages.add_message(self.request, messages.SUCCESS, 'Thank you for relocating!')
        return redirect(reverse('incident_list'))
