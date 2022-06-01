# Django imports
from django.shortcuts import get_object_or_404
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
# Local imports
from accounts.forms import UserCreationForm, EmailAndUsernameChangeForm, PasswordChangingForm, PrivacySettingsForm
from accounts.models import PrivacySettings, Profile

User = get_user_model()

class UserCreationFormTests(TestCase):

    def setUp(self):
        User.objects.create(username='TestUser3', email='validmail@mail.com', password='testpw99')

    def test_correct_form(self):
        form_data = {'username': 'TestUser1', 'email': 'testemail1@mail.com', 'password1': 'testpw99', 'password2': 'testpw99'}
        form = UserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(User.objects.filter(username="TestUser1").exists())
    
    def test_wrong_password(self):
        form_data = {'username': 'TestUser2', 'email': 'testemail2@mail.com', 'password1': 'testpw99', 'password2': 'testpw'}
        form = UserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_username_exists_handling(self):
        form_data = {'username': 'TestUser3', 'email': 'testemail3@mail.com', 'password1': 'testpw99', 'password2': 'testpw99'}
        form = UserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_email_exists_handling(self):
        form_data = {'username': 'TestUser4', 'email': 'validmail@mail.com', 'password1': 'testpw99', 'password2': 'testpw99'}
        form = UserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_profile_has_been_created(self):
        self.assertTrue(Profile.objects.filter(user=get_object_or_404(User, username="TestUser3")))

    def test_privacy_settings_have_been_created(self):
        self.assertTrue(PrivacySettings.objects.filter(profile=get_object_or_404(Profile, user__username="TestUser3")))


class EmailAndUsernameChangeFormTest(TestCase):
    
    def setUp(self):
        User.objects.create(username='TestUser1', email='testuser1@mail.com', password='testpw99')
        User.objects.create(username='TestUser2', email='testuser2@mail.com', password='testpw99')

    def test_change_username_correct(self):
        form_data = {'username': "TestUserNewName", 'email': 'testuser1@mail.com'}
        form = EmailAndUsernameChangeForm(data=form_data)
        form.instance = get_object_or_404(User, username='TestUser1')
        self.assertTrue(form.is_valid())
        form.save()
        self.assertFalse(User.objects.filter(username="TestUser1").exists())
        self.assertTrue(User.objects.filter(username="TestUserNewName").exists())

    def test_change_username_already_exists(self):
        form_data = {'username': "TestUserNewName", 'email': 'testuser1@mail.com'}
        form = EmailAndUsernameChangeForm(data=form_data)
        form.instance = get_object_or_404(User, username='TestUser2')
        self.assertFalse(form.is_valid())

    def test_change_email_correct(self):
        form_data = {'username': "TestUser1", 'email': 'testuser3@mail.com'}
        form = EmailAndUsernameChangeForm(data=form_data)
        form.instance = get_object_or_404(User, username='TestUser1')
        self.assertTrue(form.is_valid())
        form.save()
        self.assertFalse(User.objects.filter(email="testuser1@mail.com").exists())
        self.assertTrue(User.objects.filter(email="testuser3@mail.com").exists())

    def test_change_email_already_exists(self):
        form_data = {'username': "TestUser1", 'email': 'testuser2@mail.com'}
        form = EmailAndUsernameChangeForm(data=form_data)
        form.instance = get_object_or_404(User, username='TestUser2')
        self.assertFalse(form.is_valid())

class PasswordChangingFormTest(TestCase):
    
    def setUp(self):
        new_user1 = User(username="TestUser1", email="testuser1@mail.com")
        new_user1.set_password("testpw99")
        new_user1.save()

    def test_empty_form(self):
        form = PasswordChangingForm(user=get_object_or_404(User, username='TestUser1'))
        self.assertIn("old_password", form.fields)
        self.assertIn("new_password1", form.fields)
        self.assertIn("new_password2", form.fields)

    def test_new_password_too_short(self):
        form_data = {'old_password': "testpw99", 'new_password1': "newpw99", 'new_password2': "newpw99"}
        form = PasswordChangingForm(user=get_object_or_404(User, username='TestUser1'), data=form_data)
        self.assertFalse(form.is_valid())

    def test_change_password_correct(self):
        form_data = {'old_password': "testpw99", 'new_password1': "newpassword99", 'new_password2': "newpassword99"}
        form = PasswordChangingForm(user=get_object_or_404(User, username='TestUser1'), data=form_data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEquals(get_object_or_404(User, username="TestUser1").check_password("newpassword99"), True)
    
    def test_change_password_false(self):
        form_data = {'old_password': "testpw99", 'new_password1': "newpassword99", 'new_password2': "newpassword"}
        form = PasswordChangingForm(user=get_object_or_404(User, username='TestUser1'), data=form_data)
        self.assertFalse(form.is_valid())

    def test_new_password_empty(self):
        form_data = {'old_password': "testpw99", 'new_password1': "                    ", 'new_password2': "                    "}
        form = PasswordChangingForm(user=get_object_or_404(User, username='TestUser1'), data=form_data)
        self.assertFalse(form.is_valid())


class PrivacySettingsFormTest(TestCase):

    def setUp(self):
        User.objects.create(username='TestUser1', email='testuser1@mail.com', password='testpw99')

    def test_change_privacy_settings(self):
        form_data = {"list_subscribtions_public": False, 'subscribed_sources_public': True, 'highlighted_articles_public': False}
        form = PrivacySettingsForm(data=form_data)
        test_user1 = get_object_or_404(PrivacySettings, profile=get_object_or_404(Profile, user__username="TestUser1"))
        form.instance = test_user1
        self.assertTrue(form.is_valid())   
        form.save()
        self.assertFalse(test_user1.list_subscribtions_public)
        self.assertTrue(test_user1.subscribed_sources_public)
        self.assertFalse(test_user1.highlighted_articles_public)


class ProfileViewTest(TestCase):
    def setUp(self):
        User.objects.create(username='TestUser1', email='testuser1@mail.com', password='testpw99')

    def test_view(self):
        response = self.client.get(reverse('accounts:profile', kwargs={'slug': get_object_or_404(Profile, user__username="TestUser1").slug}))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'accounts/profile.html')