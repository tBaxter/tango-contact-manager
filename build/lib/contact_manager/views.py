import logging
import warnings

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, TemplateView, DetailView

from .forms import ContactForm
from .models import Contact, ContactFormController

success_url = reverse_lazy('contact_done')

# Get an instance of a logger
logger = logging.getLogger('contact_manager')


class ContactList(ListView):
    """
    Returns list of all stored messages.
    Messages are paginated according to settings.PAGINATE_BY.
    """
    template_name = 'contact/message_list.html'
    paginate_by = settings.PAGINATE_BY
    queryset = Contact.objects.filter(publish=True, site__id=settings.SITE_ID).order_by('-id')
contact_list = ContactList.as_view()


class FormContacts(ContactList):
    """
    Returns all stored comments/messages for a given
    contact form controller.
    """
    def dispatch(self, request, *args, **kwargs):
        self.controller_slug = kwargs.get('controller_slug', False)
        return super(FormContacts, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(FormContacts, self).get_queryset()
        return queryset.filter(controller__slug=self.controller_slug)
form_contact_list = FormContacts.as_view()


class ContactDone(TemplateView):
    """
    Returns simple thank you page after comment submission.
    """
    template_name = 'contact/done.html'
contact_done = ContactDone.as_view()


class ContactDetail(DetailView):
    """
    Simple contact detail view.
    """
    model = Contact
    template_name = 'contact/message_detail.html'
contact_detail = ContactDetail.as_view()


def simple_contact(request, username=""):
    """
    Defines simple contact form that can be used to
    contact a site member passed by username in the URL
    or to all superusers or to a list defined in settings.DEFAULT_CONTACTS.
    """
    site = Site.objects.get_current()
    form = ContactForm(request.POST or None)
    UserModel = get_user_model()
    recipients = []
    site_form = False

    logger.debug('Recipients should be empty: %s' % recipients)

    # if we know, fill in the user name and email
    if request.user.is_authenticated():
        # first, resolve username for tango and non-tango sites
        try:
            name = request.user.display_name
        except AttributeError:
            name = request.user.username
        form.fields['sender_name'].widget.attrs['readonly'] = 'true'
        form.fields['sender_name'].initial = name
        form.fields['sender_email'].widget.attrs['readonly'] = 'true'
        form.fields['sender_email'].initial = request.user.email

    if username:
        member = get_object_or_404(UserModel, username=username)
        recipients = [member.email, ]
        logger.debug('Recipients should be a single user: %s' % recipients)

    else:
        # site contact form.
        # Use first of settings.DEFAULT_CONTACTS or all superusers
        site_form = True
        member = None
        recipients = getattr(settings, "DEFAULT_CONTACTS", None)
        logger.debug('Recipients should be match DEFAULT_CONTACTS: %s' % recipients)

        if not recipients:
            recipients = UserModel.objects.filter(is_superuser=True).values_list('email', flat=True)
            warnings.warn(
                "settings.DEFAULT_CONTACTS does not exist. You may want to create it.",
                RuntimeWarning
            )
            logger.debug('Recipients should be superusers: %s' % recipients)

    if form.is_valid():
        if site_form:
            subject = "A {} contact form submission from {}".format(
                site.name, form.cleaned_data['sender_name']
            )
        else:
            subject = "A message from {} on {}".format(form.cleaned_data['sender_name'], site.name)
        body = form.cleaned_data['body']

        sender_email = form.cleaned_data['sender_email']

        if 'send_a_copy' in request.POST:
            recipients.append(sender_email)
            logger.debug('Recipients should be match prior + sender email: %s' % recipients)

        mail = EmailMessage(
            subject=subject,
            body=body,
            from_email=sender_email,
            to=recipients
        )
        mail.send()
        return HttpResponseRedirect(success_url)
    return render(request, 'contact/simple_form.html', {
        'form': form,
        'site': site,
        'member': member
    })


def build_contact(request, slug=""):
    """
    Builds appropriate contact form based on options
    set in the contact_form controller.
    """
    controller = get_object_or_404(ContactFormController, slug=slug)
    site = Site.objects.get_current()
    UserModel = get_user_model()
    user = request.user
    form = ContactForm(request.POST or None, request.FILES or None, controller=controller)

    # if we know, fill in the user name and email
    if user.is_authenticated():
        # first, resolve username for tango and non-tango sites
        try:
            name = user.display_name
        except AttributeError:
            name = user.username
        form.fields['sender_name'].widget.attrs['readonly'] = 'true'
        form.fields['sender_name'].initial = name
        form.fields['sender_email'].widget.attrs['readonly'] = 'true'
        form.fields['sender_email'].initial = user.email

    if form.is_valid():
        if controller.store_in_db:
            # To do: sanitize submission.
            new_msg = Contact(**form.cleaned_data)
            new_msg.controller = controller
            new_msg.site = site
            if controller.override_subject:  # we're overriding the subject
                new_msg.subject = controller.override_subject
            new_msg.save()

        if controller.send_emails:
            form_data = form.cleaned_data
            if controller.override_subject:
                subject = controller.override_subject
            elif 'subject' in form_data:
                subject = form_data['subject']
            else:
                subject = "{} message from {}".format(controller.name, form_data['sender_name'])

            body = "{} \n\n {}".format(form_data['body'], form_data['sender_name'])
            if controller.request_contact_info:
                body += "\nAddress: {} \nCity: {} \nState: {} \nPhone: {}".format(
                    form_data['contact_address'],
                    form_data['contact_city'],
                    form_data['contact_state'],
                    form_data['contact_phone']
                )

            if controller.email_options == '2':  # Create selectable list from recipients
                try:
                    to = [UserModel.objects.get(username=form.cleaned_data['to']).email]
                except Exception:
                    to = [form.cleaned_data['to']]

            if controller.email_options == '1':
                to = [r.email for r in controller.recipients.all()]
                for r in controller.other_recipients.all():
                    to.append(r.email)

            if 'send_a_copy' in form.cleaned_data:
                to.append(form.cleaned_data['sender_email'])

            mail = EmailMessage(
                subject=subject,
                body=body,
                from_email=form.cleaned_data['sender_email'],
                to=to
            )
            if 'photo' in request.FILES:
                photo = request.FILES['photo']
                mail.attach(photo.name, photo.read(), photo.content_type)
            mail.send()
        return render(request, 'success_url', {'controller': controller})

    return render(request, 'contact/form.html', {
        'form': form,
        'site': site,
        'controller': controller
    })
