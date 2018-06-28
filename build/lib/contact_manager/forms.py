
from collections import OrderedDict

from django import forms

from .models import Contact


class ContactForm(forms.ModelForm):
    """
    Builds either base contact form
    or more sophisticated form if a contact form controller is used.
    """
    required_css_class = 'required'

    class Meta:
        model = Contact
        fields = [
            'sender_name',
            'sender_email',
            'body',
            'send_a_copy',
            'contact_address',
            'contact_city',
            'contact_state',
            'contact_phone'
        ]

    def __init__(self, *args, **kwargs):
        #pick controller off before init
        controller = kwargs.get('controller', None)
        kwargs.pop("controller", None)
        super(ContactForm, self).__init__(*args, **kwargs)

        if controller:
            self.fields['sender_name'].label = "Your name"
            self.fields['sender_email'].label = "Your e-mail address"
            self.fields['body'].label = "Your message"

            # Cast self.fields out of an OrderedDict
            # so we can insert new fields.
            # We're forcing list for py3.
            insertable_fields = list(self.fields.items())

            if controller.send_emails:
                # build recipient_list from staff recipients and other recipients
                to_choices = [(r.username, r.get_full_name()) for r in controller.recipients.all()]
                for r in controller.other_recipients.all():
                    to_choices.append((r.name, r.email))
                # if 'Create selectable list of recipients' is selected, add to form
                if controller.email_options == '2':
                    insertable_fields.insert(0, ('to', forms.ChoiceField(choices=to_choices)))

            if controller.ask_for_subject:
                insertable_fields.insert(0, ('subject', forms.CharField()))

            # Now cast back to an OrderedDict
            # because we're done inserting.
            self.fields = OrderedDict(insertable_fields)

            if controller.subject_label:  # we're overriding the subject label
                self.fields['subject'].label = controller.subject_label

            if controller.body_label:  # we're overriding the body label
                self.fields['body'].label = controller.body_label

            # If there's a file
            if controller.allow_uploads:
                self.fields.append('photo')

        # if we want contact info
        if controller and controller.request_contact_info:
            self.fields['contact_address'].required = True
            self.fields['contact_city'].required = True
            self.fields['contact_state'].required = True
            self.fields['contact_phone'].required = True
        else:
            self.fields['contact_address'].widget = forms.HiddenInput()
            self.fields['contact_city'].widget = forms.HiddenInput()
            self.fields['contact_state'].widget = forms.HiddenInput()
            self.fields['contact_phone'].widget = forms.HiddenInput()
