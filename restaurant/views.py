from django.views.generic import ListView,DeleteView
from .models import Restaurant
from .forms import RestaurantFilterForm
from django.db.models.functions import Upper
from django.db.models import Q
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
            self.filterqueryset()

            if self.sort_by:
                self.sortqueryset()

        return self.queryset                

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['cities'] = Restaurant.objects.annotate(upper_location=Upper('location')).values_list('upper_location', flat=True).distinct()
        context['form']=RestaurantFilterForm(self.request.GET)
        return context
    

    
