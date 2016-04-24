from django import forms
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.forms import widgets
from .models import Comment, IncidentReport


class PollingPlaceLookupWidget(widgets.MultiWidget):
    # this is quite a hacky / treacherous abuse of MultiWidget,
    # but, it works for now. :D

    def __init__(self, attrs=None):
        super(PollingPlaceLookupWidget, self).__init__([widgets.HiddenInput, widgets.TextInput], attrs)

    # def decompress(self, value):
    #     pass

    def value_from_datadict(self, data, files, name):
        return data.get(name)

    def id_for_label(self, id_):
        return id_ +  "_display"

    def render(self, name, value, attrs=None):

        # render the hidden input (to have the title)
        hidden_input_html = self.widgets[0].render(name, value, attrs)

        # render the text input (for the user)
        # make the ID match the label for accessibility win
        # and rename the field name so we don't clobber it on the backend
        display_text_html = self.widgets[1].render(name + "_display", value, \
                                    dict(attrs, **{'id': 'id_' + name + "_display"}))

        list_wrapper = '<div id="polling_locations_list" class="list-group" style="display: none;"></div>' + \
            '<div id="pp_template" class="list-group-item" style="display: none;"><a href="#"><b data-bind="pollinglocation"></b> <span data-bind="addr"></span>, <span data-bind="city"></span> &mdash; <span data-bind="precinctname"></span></a></div>'
        
        # UI help
        help_text_html = """
                <p class="help-block">You can <a href="#" id="geolocationLink">find
                    the nearest polling location based on your
                    current location</a>, or type in the name
                    of your polling location above to search, and choose
                    from a list.</p>
            """

        # and, the real star of the show
        polling_location_script_tag = "<script type=\"text/javascript\" src=\"%s\"></script>" % static('js/pollingplaces.js')
        
        return ''.join([hidden_input_html, display_text_html, list_wrapper, \
                        help_text_html, polling_location_script_tag])


class IncidentReportForm(forms.ModelForm):

    class Meta:
        model = IncidentReport
        fields = ['nature', 'long_line', 'scope', 'polling_location',
                    'reporter_name', 'reporter_phone', 'creator_name',
                    'creator_email', 'creator_phone', 'assignee', 'description']
        widgets = {
            'polling_location': PollingPlaceLookupWidget,
            'creator': widgets.HiddenInput,
            'assignee': widgets.HiddenInput
        }
        labels = {
            'long_line': 'This incident involves a long line.',
            'creator_name': 'Your Name',
            'creator_email': 'Your Email',
            'creator_phone': 'Your Phone'
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['author', 'message', 'incident_report']
        widgets = {
            'author': widgets.HiddenInput,
            'incident_report': widgets.HiddenInput,
            'message': widgets.Textarea(attrs={'rows': 3})
        }
        labels = {
            'message': "Comment"
        }