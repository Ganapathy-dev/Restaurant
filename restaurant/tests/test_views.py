from django.test import TestCase
from django.urls import reverse,resolve
from ..models import Restaurant
from ..views import RestaurantListView
from ..forms import RestaurantFilterForm
from django.contrib.auth.models import User
from unittest.mock import patch
from datetime import time,datetime

class RestaurantListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.testuser=User.objects.create_user(username='testuser1',email='testuser1@gmail.com',password='user1@123')
        Restaurant.objects.create(
            title='Restaurant A',owner=cls.testuser,location='City A', food_type='veg', rating=4.5, cost_of_two=500, open_time='10:00', close_time='20:00'
        )
        Restaurant.objects.create(
            title='Restaurant B',owner=cls.testuser, location='City B', food_type='non_veg', rating=3.8, cost_of_two=700, open_time='11:00', close_time='20:00'
        )
        Restaurant.objects.create(
            title='Restaurant C',owner=cls.testuser, location='City A', food_type='veg', rating=4.9, cost_of_two=1000, open_time='09:00', close_time='23:00'
        )

    def test_restaurant_list_url_resolves_restaurant_list_view(self):
        view=resolve('/')
        self.assertEqual(view.func.view_class,RestaurantListView)
    
    def test_view_uses_correct_template(self):
        response=self.client.get(reverse('restaurant_list'))
        self.assertTemplateUsed(response,'restaurant/restaurant_list.html')

    def test_restaurant_list_view_context(self):
        response = self.client.get(reverse('restaurant_list')) 
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], RestaurantFilterForm)
        self.assertIn('cities', response.context)
        cities = response.context['cities']
        self.assertEqual(list(cities), ['CITY A', 'CITY B'])  
        self.assertIn('restaurants', response.context)
        self.assertEqual(len(response.context['restaurants']), 3)

    def test_filter_form_valid(self):
        response=self.client.get(reverse('restaurant_list'),{
            'city': 'City A',
            'food_type': 'veg',
            'rating': 4,
            'cost_of_two': 500
        })
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.context['restaurants']),2)

    def test_filter_by_city(self):
        response = self.client.get(reverse('restaurant_list'), {'city': 'City A'})
        self.assertEqual(len(response.context['restaurants']), 2) 
    
    def test_filter_by_food_type(self):
        response = self.client.get(reverse('restaurant_list'), {'food_type': 'non_veg'})
        self.assertEqual(len(response.context['restaurants']), 1)
        response = self.client.get(reverse('restaurant_list'), {'food_type': 'veg'})
        self.assertEqual(len(response.context['restaurants']), 2)

    def test_sort_by_rating(self):
        response = self.client.get(reverse('restaurant_list'), {'sort_by': 'rating', 'sort_order': 'high to low'})
        restaurants = response.context['restaurants']
        self.assertEqual(float(restaurants[0].rating), 4.9) 
        self.assertEqual(float(restaurants[1].rating),4.5)
    
    def test_sort_by_cost(self):
        response = self.client.get(reverse('restaurant_list'), {'sort_by': 'cost_of_two', 'sort_order': 'low to high'})
        restaurants = response.context['restaurants']
        self.assertEqual(restaurants[0].cost_of_two, 500)
        self.assertEqual(restaurants[1].cost_of_two,700)

    def test_filter_by_is_open(self):
        with patch('django.utils.timezone.now',return_value=datetime(2024,1,1,22,30)):
            response = self.client.get(reverse('restaurant_list'), {'is_open': True})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context['restaurants']), 1)