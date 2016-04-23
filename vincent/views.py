from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import CreateView, DetailView, ListView, View
from django.views.generic.base import ContextMixin


from .forms import CommentForm, IncidentReportForm
from .models import Comment, GeocodedPollingLocation, IncidentReport

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
        return IncidentReport.objects.filter(assignee=self.request.user).select_related('polling_location')


class CommentCreate(CreateView):
    model = Comment
    form_class = CommentForm

    def get_initial(self):
        return {'author': self.request.user}

    def get_success_url(self):
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
        return {'creator_name': self.request.user.get_full_name(),
                'creator_email': self.request.user.email,
                'creator': self.request.user,
                'assignee': self.request.user }


class PollingPlace(View):
    DISTANCE_IN_MILES = 5

    def text_search(self, request, *args, **kwargs):
        filters = Q()
        for field in ['pollinglocation', 'addr', 'city', 'state', 'zip']:
            filters = filters | Q(**{'%s__icontains' % field: self.q})
        return self.get_json_response_from_filters(filters)

    def geo_lookup(self, request, *args, **kwargs):
        point = Point(x=float(self.lng), y=float(self.lat), srid=4326)
        return self.get_json_response_from_filters(Q(geom__distance_lte=(point, D(mi=self.DISTANCE_IN_MILES))))

    def get_json_response_from_filters(self, filters):
        polling_locations = [loc for loc in GeocodedPollingLocation.objects.filter(filters).values('precinctid', 'pollinglocation', 'addr', 'city', 'state', 'zip')]
        return JsonResponse(data=polling_locations, safe=False)

    def get(self, request, *args, **kwargs):
        self.q = request.GET.get('q', None)
        self.lat = request.GET.get('lat', None)
        self.lng = request.GET.get('lng', None)

        if self.q:
            return self.text_search(request, *args, **kwargs)

        elif (self.lat and self.lng):
            return self.geo_lookup(request, *args, **kwargs)
        
        return JsonResponse(data={'error': 'Missing either `q` search parameter, or `lat` and `lng`.'})
