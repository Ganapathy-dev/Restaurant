from django.contrib import admin
from .models import Restaurant,Dish,Review,RestaurantImage
# Register your models here.

class DishInline(admin.TabularInline):
    model=Dish
    fields=[('name','food_type'),('price','cuisine')]
    extra=1

class ReviewInline(admin.StackedInline):
    model=Review
    fields=[('user','rating'),'comment']
    extra=0

class RestaurantImageInline(admin.TabularInline):
    model=RestaurantImage
    extra=1

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display=['title','location','cost_of_two','rating','is_spotlight']
    list_filter=['is_spotlight','food_type','cuisines']
    search_fields=['title','location',]
    list_editable=['cost_of_two']
    fields=[('title','location'),'address',('open_time','close_time'),('rating','cost_of_two'),('food_type','cuisines'),('is_spotlight','owner')]
    inlines=[RestaurantImageInline,ReviewInline,DishInline]


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display=['restaurant','name','food_type','price','cuisine']
    list_filter=['food_type','cuisine']
    search_fields=['name','restaurant']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display=['restaurant','user','comment','rating']


