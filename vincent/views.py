from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import DetailView, ListView

from .models import IncidentReport

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
    pass
    
    def get_queryset(self):
        return IncidentReport.objects.filter(assignee=self.request.user)


class IncidentDetail(DetailView):
    model = IncidentReport