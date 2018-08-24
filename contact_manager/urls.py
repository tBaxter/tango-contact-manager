from django.urls import path

from .views import simple_contact, contact_done, contact_list, contact_detail, \
    build_contact, form_contacts

urlpatterns = [
    # forms
    path('', simple_contact, name="site_contact_form"),
    path('members/<username>/', simple_contact, name="member_contact_form"),
    path('done/', contact_done, name="contact_done"),
    
    # list & detail
    path('messages/', contact_list, name="contact_list"),
    path('messages/<int:pk>/', contact_detail, name='contact_detail'),
    
    # Constructed contact forms (from controller options)
    path('<slug:slug>/', build_contact, name="contact_form_builder" ),
    path('<slug:controller_slug>/messages/', form_contacts, name="controller_contact_list"),
]
