from django.urls import path

from .views import simple_contact, ContactDone, ContactList, ContactDetail, \
    build_contact, FormContacts

urlpatterns = [
    # forms
    path('', simple_contact, name="site_contact_form"),
    path('members/<username>/', simple_contact, name="member_contact_form"),
    path('done/', ContactDone, name="contact_done"),
    
    # list & detail
    path('messages/', ContactList, name="contact_list"),
    path('messages/<int:pk>/', ContactDetail, name='contact_detail'),
    
    # Constructed contact forms (from controller options)
    path('<slug:slug>/', build_contact, name="contact_form_builder" ),
    path('<slug:controller_slug>/messages/', FormContacts, name="controller_contact_list"),
]
