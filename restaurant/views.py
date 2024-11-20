from django.views.generic import ListView,DeleteView,UpdateView
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse,reverse_lazy
from .models import Restaurant, BookmarkedRestaurant, VisitedRestaurant
from django.contrib.auth.models import User
from .forms import RestaurantFilterForm,ReviewForm,UserRegistrationForm
from django.db.models.functions import Upper
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.contrib.auth import login
from django.views.generic.edit import FormView
# Create your views here.

class RestaurantListView(ListView):
    model=Restaurant
    template_name='restaurant/restaurant_list.html'
    context_object_name='restaurants'

    def collectformdata(self):
            self.city=self.form.cleaned_data.get('city')
            self.food_type=self.form.cleaned_data.get('food_type')
            self.cuisines=self.form.cleaned_data.get('cuisines')
            self.rating=self.form.cleaned_data.get('rating')
            self.cost_of_two=self.form.cleaned_data.get('cost_of_two')
            self.is_open=self.form.cleaned_data.get('is_open')
            self.sort_by=self.form.cleaned_data.get('sort_by')
        
    def filterqueryset(self):
            if self.city:
                self.queryset=self.queryset.filter(location__icontains=self.city)

            if self.food_type:
                query=Q()
                for type in self.food_type:
                     query |= Q(food_type__iregex=rf'(^|,){type}(,|$)')
                self.queryset=self.queryset.filter(query)

            if self.cuisines:
                query=Q()
                for cuisine in self.cuisines:
                    query |=Q(cuisines__icontains=cuisine)
                self.queryset=self.queryset.filter(query)
            
            if self.rating:
                self.queryset=self.queryset.filter(rating__gte=self.rating)

            if self.cost_of_two:
                self.queryset=self.queryset.filter(cost_of_two__gte=self.cost_of_two)

            if self.is_open:
                self.queryset=[restaurant for restaurant in self.queryset if restaurant.is_open()]

        
    def sortqueryset(self):
                sort_order=self.form.cleaned_data.get('sort_order')
                if sort_order:
                    if sort_order=='high to low':
                        self.queryset=self.queryset.order_by(f'-{self.sort_by}')
                    if sort_order=='low to high':
                        self.queryset=self.queryset.order_by(self.sort_by)
                else:
                    self.queryset=self.queryset.order_by('-created_at')


    def get_queryset(self):
        self.queryset=Restaurant.objects.all()
        self.form= RestaurantFilterForm(self.request.GET)

        if self.form.is_valid():
            self.collectformdata()
            if self.sort_by:
                self.sortqueryset()
            self.filterqueryset()

        return self.queryset                

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['cities'] = Restaurant.objects.annotate(upper_location=Upper('location')).values_list('upper_location', flat=True).distinct()
        context['form']=RestaurantFilterForm(self.request.GET)
        return context
    

class RestaurantDetailView(DeleteView):
     model=Restaurant
     template_name='restaurant/restaurant_detail.html'
     context_object_name='restaurant'

     def get_context_data(self, **kwargs):
          context=super().get_context_data(**kwargs)
          context['veg_dishes']=self.object.dishes.filter(food_type='veg')
          context['non_veg_dishes']=self.object.dishes.filter(food_type='non_veg')
          context['vegan_dishes']=self.object.dishes.filter(food_type='vegan')
          if self.request.user.is_authenticated:
            context['is_bookmarked'] = self.object.bookmarkes.filter(user=self.request.user).exists()
            context['is_visited'] = self.object.visited.filter(user=self.request.user).exists()
            context['is_rated']=self.object.reviews.filter(user=self.request.user).exists()
          return context
     
     def post(self, request, *args, **kwargs):
          if self.request.user.is_authenticated:
            restaurant=self.get_object()
            form=ReviewForm(request.POST)
            if form.is_valid():
                review=form.save(commit=False)
                review.restaurant=restaurant
                review.user=request.user
                review.save()
                return redirect(reverse('restaurant_detail',kwargs={'pk':restaurant.id}))
          else:
              return HttpResponseForbidden("You must be logged-in to post a review.")
                
class ToggleBookmarkView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        restaurant_id = kwargs.get('restaurant_id')
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        bookmark, created = BookmarkedRestaurant.objects.get_or_create(
            user=request.user,
            restaurant=restaurant
        )

        if not created:
            bookmark.delete()
            is_bookmarked = False
        else:
            is_bookmarked = True

        return JsonResponse({'is_bookmarked': is_bookmarked})
    

class ToggleVisitedView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        restaurant_id = kwargs.get('restaurant_id')
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        visited, created = VisitedRestaurant.objects.get_or_create(
            user=request.user,
            restaurant=restaurant
        )

        if not created:
            visited.delete()
            is_visited = False
        else:
            is_visited = True

        return JsonResponse({'is_visited': is_visited})

class UserRegistrationView(FormView):
    template_name='accounts/user_registration.html'
    form_class=UserRegistrationForm
    success_url=reverse_lazy('restaurant_list')

    def form_valid(self, form):
        user=form.save()
        login(self.request, user)
        return super().form_valid(form)

class UserProfileUpdateView(LoginRequiredMixin,UpdateView):
    model=User
    fields=('first_name','last_name','email',)
    template_name='accounts/user_profile.html'
    success_url=reverse_lazy('my_profile')

    def get_object(self):
        return self.request.user