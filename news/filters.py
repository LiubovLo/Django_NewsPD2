import django_filters
from django_filters import FilterSet, DateTimeFilter, ModelChoiceFilter
from django.forms import DateTimeInput
from .models import Post, Category


class PostFilter(django_filters.FilterSet):
    post_title = django_filters.CharFilter(
        field_name='post_title',
        lookup_expr='icontains',
        label='Название'
    )

    post_category = django_filters.ModelChoiceFilter(
        field_name='post_category',
        lookup_expr='exact',
        queryset=Category.objects.all(),
        label='Категории'
    )

    time_create = django_filters.DateTimeFilter(
        field_name='time_create',
        lookup_expr='gt',
        widget=DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local'},
        ),
        label='Позже даты'
    )

    class Meta:
        model = Post
        fields = {
             'post_title': ['icontains'],
             'post_category': ['exact'],  # Точное совпадение категории
             'time_create': ['gt'],
         }