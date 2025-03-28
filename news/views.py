from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, PostCategory
from .filters import PostFilter
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.views.decorators.csrf import csrf_protect
from .models import Subscriber, Category
from django.shortcuts import get_object_or_404

class PostsList(ListView):
    """ Представление всех новостей в виде списка. """
    paginate_by = 10
    model = Post
    ordering = '-time_create'  # Сортировка по дате (от новых к старым)
    template_name = 'news/news_list.html'  # Шаблон для отображения
    context_object_name = 'news'  # Имя переменной в шаблоне

    def get_queryset(self):
        queryset = super().get_queryset().filter(type_post='NW')
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context

class PostDetail(DetailView):
    """ Представление одной новости. """
    model = Post
    template_name = 'news/news_detail.html'  # Шаблон для отображения
    context_object_name = 'post'  # Имя переменной в шаблоне

class SearchPosts(ListView):
    model = Post
    template_name = 'news/search.html'
    ordering = '-time_create'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class NewsCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = 'news.add_post'
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'news/news_create.html'

    def form_valid(self, form):
        news = form.save(commit=False)
        news.type_post = 'NW'
        return super().form_valid(form)


class ArticleCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = 'news.add_post'
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'news/article_create.html'

    def form_valid(self, form):
        news = form.save(commit=False)
        news.type_post = 'AR'
        return super().form_valid(form)


class NewsUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = 'news.change_post'
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'news/news_update.html'

    def form_valid(self, form):
        news = form.save(commit=False)
        news.type_post = 'NW'
        return super().form_valid(form)


class ArticleUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = 'news.change_post'
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'news/article_update.html'

    def form_valid(self, form):
        news = form.save(commit=False)
        news.type_post = 'AR'
        return super().form_valid(form)


class PostDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    permission_required = 'news.delete_post'
    raise_exception = True
    model = Post
    template_name = 'news/post_delete.html'
    success_url = reverse_lazy('news_list')

@login_required
@csrf_protect
def subscriptions(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = get_object_or_404(Category, id=category_id)
        user = request.user
        subscriber, created = Subscriber.objects.get_or_create(user=user, email=user.email)

        action = request.POST.get('action')
        if action == 'subscribe':
            Subscriber.subscribed_categories.add(category)
        elif action == 'unsubscribe':
            Subscriber.subscribed_categories.remove(category)

    categories_with_subscriptions = Category.objects.annotate(
        user_subscribed=Exists(
            Subscriber.objects.filter(
                user=request.user,
                category=OuterRef('pk'),
            )
        )
    ).order_by('name')
    return render(
        request,
        'subscriptions.html',
        {'categories': categories_with_subscriptions},
    )
# Create your views here.

