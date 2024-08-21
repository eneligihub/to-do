from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from events.models import Event, CartItem


class AddToCartTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.event = Event.objects.create(
            title='Test Event',
            name='Test Event Name',
            description='Test Event Description',
            creator=self.user,
            start_date='2024-08-19',
            end_date='2024-08-20',
            start_time='10:00:00',
            end_time='12:00:00',
            visibility=Event.PUBLIC,
            payment_type=Event.NO_PAYMENT
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

    def test_add_event_to_cart(self):
        response = self.client.get(reverse('add_to_cart', args=[self.event.id]))
        self.assertRedirects(response, reverse('user_cart'))
        self.assertTrue(CartItem.objects.filter(event=self.event, user=self.user).exists())

    def test_event_already_in_cart(self):
        CartItem.objects.create(event=self.event, user=self.user)
        response = self.client.get(reverse('add_to_cart', args=[self.event.id]))
        self.assertRedirects(response, reverse('user_cart'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'This event is already in your cart.')

    def test_cart_item_count(self):
        initial_count = CartItem.objects.count()
        self.client.get(reverse('add_to_cart', args=[self.event.id]))
        self.assertEqual(CartItem.objects.count(), initial_count + 1)