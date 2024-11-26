from django.views.generic import ListView,DeleteView
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from .models import Restaurant, BookmarkedRestaurant, VisitedRestaurant
from .forms import RestaurantFilterForm,ReviewForm
from django.db.models.functions import Upper
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from .filters import RestaurantFilter
# Create your views here.

class RestaurantListView(ListView):
    model=Restaurant
    template_name='restaurant/restaurant_list.html'
    context_object_name='restaurants'
    filterset_class=RestaurantFilter

    def get_queryset(self):
        queryset=Restaurant.objects.all()
        self.filterset=self.filterset_class(self.request.GET,queryset=queryset, request=self.request)
        return self.filterset.qs

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

