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
from .tasks import notify_about_new_post
from django.core.cache import cache
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

    def get_object(self, *args, **kwargs):
        obj = cache.get(f'post-{self.kwargs["pk"]}', None)
        if not obj:
            obj = super().get_object(queryset=self.get_queryset())
            cache.set(f'post-{self.kwargs["pk"]}', obj)

        return obj

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
        post_title = form.cleaned_data['post_title']
        post_content = form.cleaned_data['post_content']
        author = form.cleaned_data['author']
        categories = form.cleaned_data['post_category']
        type_post = 'NW'
        post_new = Post.objects.create(type_post=type_post,
                                       post_title=post_title,
                                       post_content=post_content,
                                       author=author
                                       )
        post_new.save()

        categories_list_id = Category.objects.filter(pk__in=categories).values('id')
        for category_id in categories_list_id:
            post_new.post_category.add(category_id['id'])  # срабатывает m2m_changed
        post_new.save()
        notify_about_new_post.apply_async([post_new.pk], countdown=1)

        if form.is_valid():
            return HttpResponseRedirect(f'/news/search/{post_new.pk}')

class ArticleCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = 'news.add_post'
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'news/article_create.html'

    def form_valid(self, form):
        post_title = form.cleaned_data['post_title']
        post_content = form.cleaned_data['post_content']
        author = form.cleaned_data['author']
        categories = form.cleaned_data['post_category']
        type_post = 'AR'
        post_new = Post.objects.create(type_post=type_post,
                                       post_title=post_title,
                                       post_content=post_content,
                                       author=author
                                       )
        post_new.save()

        categories_list_id = Category.objects.filter(pk__in=categories).values('id')
        for category_id in categories_list_id:
            post_new.post_category.add(category_id['id'])  # срабатывает m2m_changed
        post_new.save()
        notify_about_new_post.apply_async([post_new.pk], countdown=1)

        if form.is_valid():
            return HttpResponseRedirect(f'/news/{post_new.pk}')


class NewsUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = 'news.change_post'
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'news/news_update.html'

    def form_valid(self, form):
        post_title = form.cleaned_data['post_title']
        post_content = form.cleaned_data['post_content']
        author = form.cleaned_data['author']
        categories = form.cleaned_data['post_category']
        type_post = 'NW'
        post_updated = self.object
        post_updated.type_post = type_post
        post_updated.post_title = post_title
        post_updated.post_content = post_content
        post_updated.author = author
        post_updated.save()

        category_list = Category.objects.filter(pk__in=categories)

        PostCategory.objects.filter(post=post_updated).delete()  # удаляем все предыдущие категории

        # в цикле добавляем новые категории, при этом m2m_changed не срабатывает, т.к. поле manytomany
        # (post_updated.post_category) не затрагивается.

        for category in category_list:
            post_category = PostCategory.objects.create(post=post_updated, category=category)
            post_category.save()

        if form.is_valid():
            return HttpResponseRedirect(f'/news/search/{post_updated.pk}')


class ArticleUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = 'news.change_post'
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'news/article_update.html'

    def form_valid(self, form):
        post_title = form.cleaned_data['post_title']
        post_content = form.cleaned_data['post_content']
        author = form.cleaned_data['author']
        categories = form.cleaned_data['post_category']
        type_post = 'AR'
        post_updated = self.object
        post_updated.type_post = type_post
        post_updated.post_title = post_title
        post_updated.post_content = post_content
        post_updated.author = author
        post_updated.save()

        category_list = Category.objects.filter(pk__in=categories)

        PostCategory.objects.filter(post=post_updated).delete()           # удаляем все предыдущие категории

        # в цикле добавляем новые категории, при этом m2m_changed не срабатывает, т.к. поле manytomany
        # (post_updated.post_category) не затрагивается.

        for category in category_list:
            post_category = PostCategory.objects.create(post=post_updated, category=category)
            post_category.save()

        if form.is_valid():
            return HttpResponseRedirect(f'/news/{post_updated.pk}')


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

