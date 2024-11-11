from django.contrib import admin
from .models import Restaurant
# Register your models here.

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display=['title','location','cost_of_two','rating','is_spotlight']
    list_filter=['is_spotlight','food_type','cuisines']
    search_fields=['title','location',]
    list_editable=['cost_of_two']
    fields=[('title','location'),'address',('open_time','close_time'),('rating','cost_of_two'),('food_type','cuisines'),('is_spotlight','owner')]

