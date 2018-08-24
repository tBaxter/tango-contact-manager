from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import ContactFormController, Contact

UserModel = get_user_model()


class TestContactViews(TestCase):
    fixtures = ['auth_users.json', 'contact_form.json']

    def setUp(self):
        self.user = UserModel.objects.all()[0]
        self.username = self.user.username

    def test_admin_contact(self):
        """
        Test simple site admin contact form
        """
        form_url = reverse('site_contact_form')
        response = self.client.get(form_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue('site' in response.context)
        form_fields = response.context['form'].fields
        self.assertEquals(
            list(form_fields.keys()),
            ['sender_name', 'sender_email', 'body', 'send_a_copy',
                'contact_address', 'contact_city', 'contact_state', 'contact_phone']
        )
        # because this is a simple form these fields should be hidden:
        hidden_fields = [k.name for k in response.context['form'].hidden_fields()]
        self.assertEquals(
            hidden_fields,
            ['contact_address', 'contact_city', 'contact_state', 'contact_phone']
        )

    def test_admin_contact_post(self):
        """
        Test simple site admin contact form post submission.
        """
        form_url = reverse('site_contact_form')
        response = self.client.post(form_url)
        self.assertEqual(response.status_code, 200)

    def test_invalid_user(self):
        """
        Test invalid user does not resolve
        """
        invalid_user_url = reverse('member_contact_form', args=('invalid-username',))
        response = self.client.get(invalid_user_url)
        self.assertEqual(response.status_code, 404)
    
    def test_valid_user(self):
        """
        Test valid user resolves with form
        """
        valid_user_url = reverse('member_contact_form', args=(self.username,))
        response = self.client.get(valid_user_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue('site' in response.context)

    def test_member_contact_post(self):
        """
        Test simple site member contact form post submission.
        """
        response = self.client.post(reverse('member_contact_form', args=[self.username]))
        self.assertEqual(response.status_code, 200)

    def test_contact_list(self):
        """
        Test contact_list_messages
        """
        response = self.client.get(reverse('contact_list'))
        self.assertEqual(response.status_code, 200)
        # test passing for a controller.
        controller = ContactFormController.objects.latest('id')
        response = self.client.get(reverse('controller_contact_list', args=[controller.slug]))
        self.assertEqual(response.status_code, 200)

    def test_contact_detail(self):
        """
        Test contact_detail
        """
        response = self.client.get(reverse('contact_detail', args=[99999999999999]))
        self.assertEqual(response.status_code, 404)
        contact = Contact.objects.get(id=1)
        response = self.client.get(reverse('contact_detail', args=[contact.id]))
        self.assertEqual(response.status_code, 200)

    def test_contact_builder(self):
        """
        Test contact_form_builder
        """
        response = self.client.get(
            reverse('contact_form_builder', args=['not-a-valid-controller-slug', ])
        )
        self.assertEqual(response.status_code, 404)
        contact_form_slug = ContactFormController.objects.get(id=1).slug
        response = self.client.get(reverse('contact_form_builder', args=[contact_form_slug, ]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue('site' in response.context)
        self.assertTrue('controller' in response.context)
        form_dict = response.context['form'].__dict__
        # if user is not logged in, initial should be empty.
        self.assertEquals(len(form_dict['initial']), 0)

        self.assertTrue('contact_address' in form_dict['fields'])
        self.assertTrue('contact_city' in form_dict['fields'])
        self.assertTrue('contact_state' in form_dict['fields'])
        self.assertTrue('contact_phone' in form_dict['fields'])
        # request_contact_info is true in the fixture, therefore
        self.assertTrue(form_dict['fields']['contact_address'].required)
        self.assertTrue(form_dict['fields']['contact_city'].required)
        self.assertTrue(form_dict['fields']['contact_state'].required)
        self.assertTrue(form_dict['fields']['contact_phone'].required)

    def test_contact_builder_authenticated(self):
        contact_form_slug = ContactFormController.objects.get(id=1).slug
        test_user = get_user_model().objects.create_user('test', 'testy@test.com', 't3stp@s$')
        self.client.login(username=test_user.username, password=test_user.password)
        response = self.client.get(reverse('contact_form_builder', args=[contact_form_slug, ]))
        self.assertEqual(response.status_code, 200)
        #form_dict = response.context['form'].__dict__
        #self.assertTrue(response.context['user'].is_authenticated
        #self.assertEqual(form_dict['fields']['sender_name'].initial, self.username)
        #self.assertEqual(form_dict['fields']['sender_email'].initial, self.user.email)
