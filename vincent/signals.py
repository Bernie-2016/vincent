from django.contrib.auth.signals import user_logged_in
from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.shortcuts import redirect

@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    if request.current_app == 'admin':
        import pdb; pdb.set_trace()
        return redirect('admin:vincent_incidentreport_changelist')