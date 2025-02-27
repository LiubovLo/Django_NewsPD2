from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Post

class PostsList(ListView):
    """ Представление всех новостей в виде списка. """
    paginate_by = 3
    model = Post
    ordering = '-time_create'  # Сортировка по дате (от новых к старым)
    template_name = 'news/news_list.html'  # Шаблон для отображения
    context_object_name = 'news'  # Имя переменной в шаблоне

    def get_queryset(self):
        """ Возвращаем только новости (не статьи). """
        return Post.objects.filter(type_post='NW').order_by('-time_create')
class PostDetail(DetailView):
    """ Представление одной новости. """
    model = Post
    template_name = 'news/news_detail.html'  # Шаблон для отображения
    context_object_name = 'post'  # Имя переменной в шаблоне
# Create your views here.

